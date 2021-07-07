from mDateTime import cDate, cDateDuration;

# The rest of the imports are at the end to prevent import loops.

def fxConvertFromJSONData(xStructureDetails, xJSONData, sDataNameInError, s0BasePath, dxInheritingValues):
  if xStructureDetails is None:
    if xJSONData is not None:
      raise cJSONDataTypeException(
        "%s should be None, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return None;
  elif isinstance(xStructureDetails, cDataStructure):
    return xStructureDetails.fxConvertFromJSONData(xJSONData, sDataNameInError, s0BasePath, dxInheritingValues);
  elif isinstance(xStructureDetails, tuple):
    # A tuple means a list of possible structures; try each until we find one that works:
    asErrorMessages = [];
    for xPossibleStructure in xStructureDetails:
      try:
        return fxConvertFromJSONData(xPossibleStructure, xJSONData, sDataNameInError, s0BasePath, dxInheritingValues);
      except cJSONDataTypeException as oException:
        asErrorMessages.append(oException.sMessage);
    raise cJSONDataTypeException(
      "%s cannot be parsed in any known way: %s" % (sDataNameInError, ", ".join(asErrorMessages)),
      {"sName": sDataNameInError, "xValue": xJSONData},
    );
  elif isinstance(xStructureDetails, dict):
    if not isinstance(xJSONData, dict):
      raise cJSONDataTypeException(
        "%s should contain a dictionary, not %s" % (sDataNameInError, type(xJSONData).__name__),
      {"sName": sDataNameInError, "xValue": xJSONData},
    );
    dxStructureDetails_by_sChildName = xStructureDetails;
    xStructureDetailsForUnspecifiedChildren = dxStructureDetails_by_sChildName.get("*");
    asRequiredChildNames = [s for s in dxStructureDetails_by_sChildName.keys() if s != "*" and s[0] != "?"];
    asOptionalChildNames = [s[1:] for s in dxStructureDetails_by_sChildName.keys() if s != "*" and s[0] == "?"];
    dxData = {};
    # We will process inheriting values first, so that they can be updated before we process the remaining
    axOrderedChildren = (
      [(sChildName, xChildValue) for (sChildName, xChildValue) in xJSONData.items() if sChildName in dxInheritingValues] + 
      [(sChildName, xChildValue) for (sChildName, xChildValue) in xJSONData.items() if sChildName not in dxInheritingValues]
    );
    for (sChildName, xChildValue) in axOrderedChildren:
      if sChildName in asRequiredChildNames:
        xChildStructureDetails = dxStructureDetails_by_sChildName[sChildName];
        asRequiredChildNames.remove(sChildName);
      elif sChildName in asOptionalChildNames:
        xChildStructureDetails = dxStructureDetails_by_sChildName["?" + sChildName];
        asOptionalChildNames.remove(sChildName);
      elif sChildName in dxInheritingValues:
        # Missing value is not a problem if it can be inherited:
        dxData[sChildName] = dxInheritingValues[sChildName];
        # We applied a value directly, not an xStructureDetails, so there is no
        # need to parse it: we can continue immediately:
        continue;
      elif xStructureDetailsForUnspecifiedChildren:
        xChildStructureDetails = xStructureDetailsForUnspecifiedChildren;
      else:
        raise cJSONDataTypeException(
          "%s contains a superfluous value named %s" % (sDataNameInError, repr(sChildName)),
          {"sName": sDataNameInError, "xValue": xJSONData},
        );
      sChildNameInErrors = "%s.%s" % (sDataNameInError, sChildName);
      dxData[sChildName] = fxConvertFromJSONData(xChildStructureDetails, xChildValue, sChildNameInErrors, s0BasePath, dxInheritingValues);
      if sChildName in dxInheritingValues and dxInheritingValues[sChildName] != dxData[sChildName]:
        # If an inherited value is modified children will inherit the modified value:
        dxInheritingValues[sChildName] = dxData[sChildName];
    # We may have to inherit required child names:
    for sChildName in asRequiredChildNames[:]: # loop on a copy as we are modifying the original.
      if sChildName in dxInheritingValues:
        dxData[sChildName] = dxInheritingValues[sChildName];
        asRequiredChildNames.remove(sChildName);
    # All required names should have been found and removed. If any still exist, report one of them:
    if asRequiredChildNames:
      raise cJSONDataTypeException(
        "%s is missing a value named %s" % (sDataNameInError, repr(asRequiredChildNames[0])),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return dxData;
  elif isinstance(xStructureDetails, list):
    if not isinstance(xJSONData, list):
      raise cJSONDataTypeException(
        "%s should contain a list not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    if len(xStructureDetails) > 1 and len(xJSONData) != len(xStructureDetails):
      raise cJSONDataTypeException(
        "%s should contain a list with %d values, not %d" % (sDataNameInError, len(xStructureDetails), len(xJSONData)),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    axData = [];
    for uIndex in range(len(xJSONData)):
      xElementStructureDetails = xStructureDetails[len(xStructureDetails) > 1 and uIndex or 0];
      sElementNameInErrors = "%s[%d]" % (sDataNameInError, uIndex);
      axData.append(fxConvertFromJSONData(xElementStructureDetails, xJSONData[uIndex], sElementNameInErrors, s0BasePath, dxInheritingValues));
    return axData;
  elif xStructureDetails == "boolean":
    if not isinstance(xJSONData, bool):
      raise cJSONDataTypeException(
        "%s should be boolean, not %s" % (sDataNameInError, repr(xJSONData)),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return xJSONData;
  elif xStructureDetails == "unsigned integer":
    if not isinstance(xJSONData, int) or xJSONData < 0:
      raise cJSONDataTypeException(
        "%s should be an unsigned integer, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return int(xJSONData);
  elif xStructureDetails == "signed integer":
    if not isinstance(xJSONData, int):
      raise cJSONDataTypeException(
        "%s should be an integer, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return int(xJSONData);
  elif xStructureDetails == "string":
    if not isinstance(xJSONData, str):
      raise cJSONDataTypeException(
        "%s should be a string, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return xJSONData;
  elif xStructureDetails == "ascii":
    if not isinstance(xJSONData, str):
      raise cJSONDataTypeException(
        "%s should be an ascii string, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return bytes(xJSONData, "ascii", "strict");
  elif xStructureDetails.startswith("string:"):
    if not isinstance(xJSONData, str):
      raise cJSONDataTypeException(
        "%s should be a string, not %s" % (sDataNameInError,  type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    sExpectedString = xStructureDetails[7:];
    if str(xJSONData) != sExpectedString:
      raise cJSONDataTypeException(
        "%s should be the string %s, not %s" % (sDataNameInError, repr(sExpectedString), repr(xJSONData)),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return sExpectedString;
  elif xStructureDetails == "path":
    if not isinstance(xJSONData, str):
      raise cJSONDataTypeException(
        "%s should be a path string, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return str(os.path.join(s0BasePath or "", xJSONData));
  elif xStructureDetails == "date":
    if not isinstance(xJSONData, str):
      raise cJSONDataTypeException(
        "%s should be a date string, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    oDate = cDate.foFromJSON(xJSONData);
    return oDate;
  elif xStructureDetails == "duration":
    if not isinstance(xJSONData, str):
      raise cJSONDataTypeException(
        "%s should be a duration string, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    oDateDuration = cDateDuration.foFromJSON(xJSONData);
    return oDateDuration;
  elif xStructureDetails == "version":
    o0Version = cVersion.fo0FromString(xJSONData) if isinstance(xJSONData, str) else None;
    if not o0Version:
      raise cJSONDataTypeException(
        "%s should be a version string, not %s" % (sDataNameInError, type(xJSONData).__name__),
        {"sName": sDataNameInError, "xValue": xJSONData},
      );
    return o0Version;
  raise AssertionError("Unhandled structure type %s" % repr(xStructureDetails));

from .cDataStructure import cDataStructure;
from .cVersion import cVersion;
from .mExceptions import *;


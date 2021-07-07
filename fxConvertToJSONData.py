from mDateTime import cDate, cDateDuration;

# The rest of the imports are at the end to prevent import loops.

def fxConvertToJSONData(xStructureDetails, xData, sDataNameInError, s0BasePath, dxInheritingValues):
  if isinstance(xStructureDetails, cDataStructure):
    return xStructureDetails.fxConvertToJSONData(xData, sDataNameInError, s0BasePath, dxInheritingValues);
  elif isinstance(xStructureDetails, tuple):
    asErrorMessages = [];
    for xPossibleStructure in xStructureDetails:
      try:
        return fxConvertToJSONData(xPossibleStructure, xData, sDataNameInError, s0BasePath, dxInheritingValues);
      except cJSONDataTypeException as oException:
        asErrorMessages.append(oException.sMessage);
    raise cJSONDataTypeException(
      "%s should have a valid value, not %s (%s)" % (sDataNameInError, repr(xData), ", ".join(asErrorMessages)),
      {"sName": sDataNameInError, "xValue": xData},
    );
  elif isinstance(xStructureDetails, dict):
    dxJSONData = {};
    for (sPropertyName, xPropertyStructureDetails) in list(xStructureDetails.items()):
      bOptional = sPropertyName[0] == "?";
      if bOptional: sPropertyName = sPropertyName[1:];
      if hasattr(xData, sPropertyName):
        xPropertyData = getattr(xData, sPropertyName);
        if not bOptional or xPropertyData is not None:
          dxJSONData[sPropertyName] = fxConvertToJSONData(
            xPropertyStructureDetails,
            xPropertyData, "%s.%s" % (sDataNameInError, sPropertyName),
            s0BasePath,
            dxInheritingValues,
          );
          if sPropertyName in dxInheritingValues:
            dxInheritingValues[sPropertyName] = dxJSONData[sPropertyName];
      elif sPropertyName in dxInheritingValues:
          dxJSONData[sPropertyName] = dxInheritingValues[sPropertyName];
      elif not bOptional:
        raise cJSONDataTypeException(
          "%s does not have a %s property." % (sDataNameInError, repr(sPropertyName)),
          {"sName": sDataNameInError, "xValue": xData},
        );
    return dxJSONData;
  elif isinstance(xStructureDetails, list):
    if not isinstance(xData, list):
      raise cJSONDataTypeException(
        "%s should contain a list, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    if len(xStructureDetails) > 1 and len(xData) != len(xStructureDetails):
      raise cJSONDataTypeException(
        "%s should contain a list with %d values, not %d" % (sDataNameInError, len(xStructureDetails), len(xJSONData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    axData = [];
    for uIndex in range(len(xData)):
      xElementStructureDetails = xStructureDetails[len(xStructureDetails) > 1 and uIndex or 0];
      sElementNameInErrors = "%s[%d]" % (sDataNameInError, uIndex);
      axData.append(fxConvertToJSONData(xElementStructureDetails, xData[uIndex], sElementNameInErrors, s0BasePath, dxInheritingValues));
    return axData;
  elif xStructureDetails == "boolean":
    if not isinstance(xData, bool):
      raise cJSONDataTypeException(
        "%s should contain a boolean, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return xData;
  elif xStructureDetails == "unsigned integer":
    if not isinstance(xData, int) or xData < 0:
      raise cJSONDataTypeException(
        "%s should contain an unsigned integer, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return int(xData);
  elif xStructureDetails == "signed integer":
    if not isinstance(xData, int):
      raise cJSONDataTypeException(
        "%s should contain an integer, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return int(xData);
  elif xStructureDetails == "string":
    if not isinstance(xData, str):
      raise cJSONDataTypeException(
        "%s should contain a string, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return xData;
  elif xStructureDetails == "ascii":
    if not isinstance(xData, bytes):
      raise cJSONDataTypeException(
        "%s should contain a bytes, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return str(xData, "ascii", "strict");
  elif xStructureDetails is None:
    if xData is not None:
      raise cJSONDataTypeException(
        "%s should have no value, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return None;
  elif xStructureDetails.startswith("string:"):
    if not isinstance(xData, str):
      raise cJSONDataTypeException(
        "%s should contain a string, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    sExpectedString = xStructureDetails[7:];
    if str(xData) != sExpectedString:
      raise cJSONDataTypeException(
        "%s should contain the string %s, not %s" % (sDataNameInError, repr(sExpectedString), repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return sExpectedString;
  elif xStructureDetails == "path":
    if not isinstance(xData, str):
      raise cJSONDataTypeException(
        "%s should contain a string, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return str(os.path.relpath(xData, s0BasePath or ""));
  elif xStructureDetails == "date":
    if not isinstance(xData, cDate):
      raise cJSONDataTypeException(
        "%s should contain a date, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return xData.fxToJSON();
  elif xStructureDetails == "duration":
    if not isinstance(xData, cDateDuration):
      raise cJSONDataTypeException(
        "%s should contain a duration, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return xData.fxToJSON();
  elif xStructureDetails == "version":
    if not isinstance(xData, cVersion):
      raise cJSONDataTypeException(
        "%s should contain a version, not %s" % (sDataNameInError, repr(xData)),
        {"sName": sDataNameInError, "xValue": xData},
      );
    return str(xData);
  raise AssertionError("Unhandled structure type %s" % repr(xStructureDetails));

from .cDataStructure import cDataStructure;
from .cVersion import cVersion;
from .mExceptions import *;


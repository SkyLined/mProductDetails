import json, os;

from .cDate import cDate;
from .cErrorException import cErrorException;
from .cVersion import cVersion;

class cDataStructure(object):
  class cSyntaxErrorException(cErrorException):
    pass;
  
  def __init__(oSelf, xStructureDetails, cConstructor = None):
    oSelf.xStructureDetails = xStructureDetails;
    oSelf.cConstructor = cConstructor;
  
  def fxParseJSON(oSelf, sJSONData, sDataNameInError, sBasePath = None):
    try:
      xJSONData = json.loads(sJSONData);
    except:
      raise cDataStructure.cSyntaxErrorException("%s does not contain valid JSON" % sDataNameInError);
    return oSelf.fxCheckAndConvertData(xJSONData, sDataNameInError, sBasePath);
    
  def fxCheckAndConvertData(oSelf, xData, sDataNameInError, sBasePath = None):
    xData = fxCheckAndConvertData(oSelf.xStructureDetails, xData, "%s root" % sDataNameInError, sBasePath);
    if oSelf.cConstructor:
      xData = oSelf.cConstructor(**xData);
    return xData;

def fxCheckAndConvertData(xStructureDetails, xData, sDataNameInError, sBasePath):
  if xStructureDetails.__class__ == cDataStructure:
    return xStructureDetails.fxCheckAndConvertData(xData, sDataNameInError, sBasePath);
  elif xStructureDetails.__class__ == tuple:
    # A tuple means a list of possible structures; try each until we find one that works:
    for xPossibleStructure in xStructureDetails:
      try:
        return fxCheckAndConvertData(xPossibleStructure, xData, sDataNameInError, sBasePath);
      except cDataStructure.cSyntaxErrorException, oSyntaxException:
        pass;
    raise cDataStructure.cSyntaxErrorException("%s should have a valid value, not %s" % (sDataNameInError, repr(xData)));
  elif xStructureDetails.__class__ == dict:
    if xData.__class__ != dict:
      raise cDataStructure.cSyntaxErrorException("%s should contain a dictionary, not %s" % (sDataNameInError, repr(xData)));
    dxStructureDetails_by_sChildName = xStructureDetails;
    xStructureDetailsForUnspecifiedChildren = dxStructureDetails_by_sChildName.get("*");
    asMissingChildNames = [s for s in dxStructureDetails_by_sChildName.keys() if s != "*"];
    dxData = {};
    for (sChildName, xChildValue) in xData.items():
      if sChildName not in asMissingChildNames:
        if not xStructureDetailsForUnspecifiedChildren:
          raise cDataStructure.cSyntaxErrorException("%s contains an unexpected value %s=%s" % \
              (sDataNameInError, repr(sChildName), repr(xChildValue)));
      else:
        asMissingChildNames.remove(sChildName);
      xChildStructureDetails = dxStructureDetails_by_sChildName.get(sChildName) or xStructureDetailsForUnspecifiedChildren;
      sChildNameInErrors = "%s.%s" % (sDataNameInError, sChildName);
      dxData[sChildName] = fxCheckAndConvertData(xChildStructureDetails, xChildValue, sChildNameInErrors, sBasePath);
    if asMissingChildNames:
      raise cDataStructure.cSyntaxErrorException("%s does not contain a value named %s" % (sDataNameInError, repr(asMissingChildNames[0])));
    return dxData;
  elif xStructureDetails.__class__ == list:
    if xData.__class__ != list:
      raise cDataStructure.cSyntaxErrorException("%s should contain a list, not %s" % (sDataNameInError, repr(xData)));
    if len(xStructureDetails) > 1 and len(xData) != len(xStructureDetails):
      raise cDataStructure.cSyntaxErrorException("%s should contain a list with %d values, not %d" % \
          (len(xStructureDetails), len(xData)));
    axData = [];
    for uIndex in xrange(len(xData)):
      xElementStructureDetails = xStructureDetails[len(xStructureDetails) > 1 and uIndex or 0];
      sElementNameInErrors = "%s[%d]" % (sDataNameInError, uIndex);
      axData.append(fxCheckAndConvertData(xElementStructureDetails, xData[uIndex], sElementNameInErrors, sBasePath));
    return axData;
  elif xStructureDetails == "boolean":
    if xData.__class__ != bool:
      raise cDataStructure.cSyntaxErrorException("%s should contain a boolean, not %s" % (sDataNameInError, repr(xData)));
    return xData;
  elif xStructureDetails == "unsigned integer":
    if xData.__class__ not in [int, long] or xData < 0:
      raise cDataStructure.cSyntaxErrorException("%s should contain an unsigned integer, not %s" % (sDataNameInError, repr(xData)));
    return long(xData);
  elif xStructureDetails == "signed integer":
    if xData.__class__ not in [int, long]:
      raise cDataStructure.cSyntaxErrorException("%s should contain an integer, not %s" % (sDataNameInError, repr(xData)));
    return long(xData);
  elif xStructureDetails == "string":
    if xData.__class__ not in [str, unicode]:
      raise cDataStructure.cSyntaxErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xData)));
    return str(xData);
  elif xStructureDetails.startswith("string:"):
    if xData.__class__ not in [str, unicode]:
      raise cDataStructure.cSyntaxErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xData)));
    sExpectedString = xStructureDetails[7:];
    if str(xData) != sExpectedString:
      raise cDataStructure.cSyntaxErrorException("%s should contain the string %s, not %s" % (sDataNameInError, repr(sExpectedString), repr(xData)));
    return sExpectedString;
  elif xStructureDetails == "path":
    if xData.__class__ not in [str, unicode]:
      raise cDataStructure.cSyntaxErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xData)));
    return str(os.path.join(sBasePath or "", xData));
  elif xStructureDetails == "date":
    oDate = xData.__class__ in [str, unicode] and cDate.foFromString(xData);
    if not oDate:
      raise cDataStructure.cSyntaxErrorException("%s should contain a date string, not %s" % (sDataNameInError, repr(xData)));
    return oDate;
  elif xStructureDetails == "version":
    oVersion = xData.__class__ in [str, unicode] and cVersion.foFromString(xData);
    if not oVersion:
      raise cDataStructure.cSyntaxErrorException("%s should contain a version string, not %s" % (sDataNameInError, repr(xData)));
    return oVersion;
  elif xStructureDetails == "-":
    if xData is not None:
      raise cDataStructure.cSyntaxErrorException("%s should have no value, not %s" % (sDataNameInError, repr(xData)));
    return None;
  raise AssertionError("Unhandled structure type %s" % repr(xStructureDetails));


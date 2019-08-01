import json, os;

from mDateTime import cDate, cDateDuration;
from .cErrorException import cErrorException;
from .cVersion import cVersion;

class cDataStructure(object):
  class cJSONSyntaxErrorException(cErrorException):
    pass;
  class cDataErrorException(cErrorException):
    pass;
  
  def __init__(oSelf, xStructureDetails, cConstructor = None):
    oSelf.xStructureDetails = xStructureDetails;
    oSelf.cConstructor = cConstructor;
    assert cConstructor is None or xStructureDetails.__class__ == dict, \
        "The structure details must be a dictionary if you want to supply a constructor.";
  
  def fxParseJSON(oSelf, sJSONData, sDataNameInError, sBasePath = None):
    try:
      xJSONData = json.loads(sJSONData);
    except:
      raise cDataStructure.cJSONSyntaxErrorException("%s does not contain valid JSON" % sDataNameInError);
    xData = oSelf.fxConvertFromJSONData(xJSONData, sDataNameInError, sBasePath);
    return xData;
    
  def fxConvertFromJSONData(oSelf, xJSONData, sDataNameInError, sBasePath = None):
    xData = fxConvertFromJSONData(oSelf.xStructureDetails, xJSONData, "%s root" % sDataNameInError, sBasePath);
    if oSelf.cConstructor:
      xData = oSelf.cConstructor(**xData);
    return xData;

  def fsStringify(oSelf, oData, sDataNameInError, sBasePath = None):
    xJSONData = oSelf.fxConvertToJSONData(oData, sDataNameInError, sBasePath);
    sJSONData = json.dumps(xJSONData, sort_keys = True, indent = 2).replace("\n", "\r\n"); # We're on Windows
    return sJSONData;
  
  def fxConvertToJSONData(oSelf, oData, sDataNameInError, sBasePath = None):
    assert oSelf.cConstructor, \
        "This function is only intended to be used for objects";
    assert oData.__class__ == oSelf.cConstructor, \
        "Please provide a %s instance in the oData argument, not %s" % \
        (oSelf.cConstructor.__name__, oData.__class__.__name__);
    return fxConvertToJSONData(oSelf.xStructureDetails, oData, sDataNameInError, sBasePath);

def fxConvertFromJSONData(xStructureDetails, xJSONData, sDataNameInError, sBasePath):
  if xStructureDetails is None:
    if xJSONData is not None:
      raise cDataStructure.cJSONSyntaxErrorException("%s should have no value, not %s" % (sDataNameInError, repr(xJSONData)));
    return None;
  elif xStructureDetails.__class__ == cDataStructure:
    return xStructureDetails.fxConvertFromJSONData(xJSONData, sDataNameInError, sBasePath);
  elif xStructureDetails.__class__ == tuple:
    # A tuple means a list of possible structures; try each until we find one that works:
    asSyntaxErrorMessages = [];
    for xPossibleStructure in xStructureDetails:
      try:
        return fxConvertFromJSONData(xPossibleStructure, xJSONData, sDataNameInError, sBasePath);
      except cDataStructure.cJSONSyntaxErrorException, oSyntaxException:
        asSyntaxErrorMessages.append(oSyntaxException.sMessage);
    raise cDataStructure.cJSONSyntaxErrorException("%s should have a valid value, not %s (%s)" % (sDataNameInError, repr(xJSONData), ", ".join(asSyntaxErrorMessages)));
  elif xStructureDetails.__class__ == dict:
    if xJSONData.__class__ != dict:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a dictionary, not %s" % (sDataNameInError, repr(xJSONData)));
    dxStructureDetails_by_sChildName = xStructureDetails;
    xStructureDetailsForUnspecifiedChildren = dxStructureDetails_by_sChildName.get("*");
    asMissingChildNames = [s for s in dxStructureDetails_by_sChildName.keys() if s != "*"];
    dxData = {};
    for (sChildName, xChildValue) in xJSONData.items():
      if sChildName not in asMissingChildNames:
        if not xStructureDetailsForUnspecifiedChildren:
          raise cDataStructure.cJSONSyntaxErrorException("%s contains an unexpected value %s=%s" % \
              (sDataNameInError, repr(sChildName), repr(xChildValue)));
      else:
        asMissingChildNames.remove(sChildName);
      xChildStructureDetails = dxStructureDetails_by_sChildName.get(sChildName) or xStructureDetailsForUnspecifiedChildren;
      sChildNameInErrors = "%s.%s" % (sDataNameInError, sChildName);
      dxData[sChildName] = fxConvertFromJSONData(xChildStructureDetails, xChildValue, sChildNameInErrors, sBasePath);
    if asMissingChildNames:
      raise cDataStructure.cJSONSyntaxErrorException("%s does not contain a value named %s" % (sDataNameInError, repr(asMissingChildNames[0])));
    return dxData;
  elif xStructureDetails.__class__ == list:
    if xJSONData.__class__ != list:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a list, not %s" % (sDataNameInError, repr(xJSONData)));
    if len(xStructureDetails) > 1 and len(xJSONData) != len(xStructureDetails):
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a list with %d values, not %d" % \
          (sDataNameInError, len(xStructureDetails), len(xJSONData)));
    axData = [];
    for uIndex in xrange(len(xJSONData)):
      xElementStructureDetails = xStructureDetails[len(xStructureDetails) > 1 and uIndex or 0];
      sElementNameInErrors = "%s[%d]" % (sDataNameInError, uIndex);
      axData.append(fxConvertFromJSONData(xElementStructureDetails, xJSONData[uIndex], sElementNameInErrors, sBasePath));
    return axData;
  elif xStructureDetails == "boolean":
    if xJSONData.__class__ != bool:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a boolean, not %s" % (sDataNameInError, repr(xJSONData)));
    return xJSONData;
  elif xStructureDetails == "unsigned integer":
    if xJSONData.__class__ not in [int, long] or xJSONData < 0:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain an unsigned integer, not %s" % (sDataNameInError, repr(xJSONData)));
    return long(xJSONData);
  elif xStructureDetails == "signed integer":
    if xJSONData.__class__ not in [int, long]:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain an integer, not %s" % (sDataNameInError, repr(xJSONData)));
    return long(xJSONData);
  elif xStructureDetails == "string":
    if xJSONData.__class__ not in [str, unicode]:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xJSONData)));
    return str(xJSONData);
  elif xStructureDetails.startswith("string:"):
    if xJSONData.__class__ not in [str, unicode]:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xJSONData)));
    sExpectedString = xStructureDetails[7:];
    if str(xJSONData) != sExpectedString:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain the string %s, not %s" % (sDataNameInError, repr(sExpectedString), repr(xJSONData)));
    return sExpectedString;
  elif xStructureDetails == "path":
    if xJSONData.__class__ not in [str, unicode]:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xJSONData)));
    return str(os.path.join(sBasePath or "", xJSONData));
  elif xStructureDetails == "date":
    if xJSONData.__class__ not in [str, unicode]:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a date string, not %s" % (sDataNameInError, repr(xJSONData)));
    oDate = cDate.foFromJSON(xJSONData);
    return oDate;
  elif xStructureDetails == "duration":
    if xJSONData.__class__ not in [str, unicode]:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a duration string, not %s" % (sDataNameInError, repr(xJSONData)));
    oDateDuration = cDateDuration.foFromJSON(xJSONData);
    return oDateDuration;
  elif xStructureDetails == "version":
    oVersion = xJSONData.__class__ in [str, unicode] and cVersion.foFromString(xJSONData);
    if not oVersion:
      raise cDataStructure.cJSONSyntaxErrorException("%s should contain a version string, not %s" % (sDataNameInError, repr(xJSONData)));
    return oVersion;
  raise AssertionError("Unhandled structure type %s" % repr(xStructureDetails));

def fxConvertToJSONData(xStructureDetails, xData, sDataNameInError, sBasePath):
  if xStructureDetails.__class__ == cDataStructure:
    return xStructureDetails.fxConvertToJSONData(xData, sDataNameInError, sBasePath);
  elif xStructureDetails.__class__ == tuple:
    for xPossibleStructure in xStructureDetails:
      try:
        return fxConvertToJSONData(xPossibleStructure, xData, sDataNameInError, sBasePath);
      except cDataStructure.cDataErrorException, oSyntaxException:
        pass;
    raise cDataStructure.cDataErrorException("%s could not be recognized: got %s" % (sDataNameInError, repr(xData)));
  elif xStructureDetails.__class__ == dict:
    dxJSONData = {};
    for (sPropertyName, xPropertyStructureDetails) in xStructureDetails.items():
      if not hasattr(xData, sPropertyName):
        raise cDataStructure.cDataErrorException("%s does not have a %s property." % (sDataNameInError, repr(sPropertyName)));
      xPropertyData = getattr(xData, sPropertyName);
      dxJSONData[sPropertyName] = fxConvertToJSONData(xPropertyStructureDetails, xPropertyData, "%s.%s" % (sDataNameInError, sPropertyName), sBasePath);
    return dxJSONData;
  elif xStructureDetails.__class__ == list:
    if xData.__class__ != list:
      raise cDataStructure.cDataErrorException("%s should contain a list, not %s" % (sDataNameInError, repr(xData)));
    if len(xStructureDetails) > 1 and len(xData) != len(xStructureDetails):
      raise cDataStructure.cDataErrorException("%s should contain a list with %d values, not %d" % \
          (sDataNameInError, len(xStructureDetails), len(xJSONData)));
    axData = [];
    for uIndex in xrange(len(xData)):
      xElementStructureDetails = xStructureDetails[len(xStructureDetails) > 1 and uIndex or 0];
      sElementNameInErrors = "%s[%d]" % (sDataNameInError, uIndex);
      axData.append(fxConvertToJSONData(xElementStructureDetails, xData[uIndex], sElementNameInErrors, sBasePath));
    return axData;
  elif xStructureDetails == "boolean":
    if xData.__class__ != bool:
      raise cDataStructure.cDataErrorException("%s should contain a boolean, not %s" % (sDataNameInError, repr(xData)));
    return xData;
  elif xStructureDetails == "unsigned integer":
    if xData.__class__ not in [int, long] or xData < 0:
      raise cDataStructure.cDataErrorException("%s should contain an unsigned integer, not %s" % (sDataNameInError, repr(xData)));
    return long(xData);
  elif xStructureDetails == "signed integer":
    if xData.__class__ not in [int, long]:
      raise cDataStructure.cDataErrorException("%s should contain an integer, not %s" % (sDataNameInError, repr(xData)));
    return long(xData);
  elif xStructureDetails == "string":
    if xData.__class__ not in [str, unicode]:
      raise cDataStructure.cDataErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xData)));
    return str(xData);
  elif xStructureDetails == None:
    if xData is not None:
      raise cDataStructure.cDataErrorException("%s should have no value, not %s" % (sDataNameInError, repr(xData)));
    return None;
  elif xStructureDetails.startswith("string:"):
    if xData.__class__ not in [str, unicode]:
      raise cDataStructure.cDataErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xData)));
    sExpectedString = xStructureDetails[7:];
    if str(xData) != sExpectedString:
      raise cDataStructure.cDataErrorException("%s should contain the string %s, not %s" % (sDataNameInError, repr(sExpectedString), repr(xData)));
    return sExpectedString;
  elif xStructureDetails == "path":
    if xData.__class__ not in [str, unicode]:
      raise cDataStructure.cDataErrorException("%s should contain a string, not %s" % (sDataNameInError, repr(xData)));
    return str(os.path.relpath(xData, sBasePath or ""));
  elif xStructureDetails == "date":
    if xData.__class__ != cDate:
      raise cDataStructure.cDataErrorException("%s should contain a date, not %s" % (sDataNameInError, repr(xData)));
    return xData.fxToJSON();
  elif xStructureDetails == "duration":
    if xData.__class__ != cDateDuration:
      raise cDataStructure.cDataErrorException("%s should contain a duration, not %s" % (sDataNameInError, repr(xData)));
    return xData.fxToJSON();
  elif xStructureDetails == "version":
    if xData.__class__ != cVersion:
      raise cDataStructure.cDataErrorException("%s should contain a version, not %s" % (sDataNameInError, repr(xData)));
    return str(xData);
  raise AssertionError("Unhandled structure type %s" % repr(xStructureDetails));

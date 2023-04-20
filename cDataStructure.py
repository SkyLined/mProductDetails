import json;

try:
  from mNotProvided import fAssertTypes as f0AssertTypes;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mNotProvided'":
    raise;
  f0AssertTypes = None;

from .mExceptions import cJSONDataSyntaxException;
# The rest of the imports are at the end to prevent import loops.

class cDataStructure(object):
  cJSONDataSyntaxException = cJSONDataSyntaxException;
  def __init__(oSelf, xStructureDetails, f0oConstructor = None):
    oSelf.xStructureDetails = xStructureDetails;
    oSelf.f0oConstructor = f0oConstructor;
    assert f0oConstructor is None or xStructureDetails.__class__ == dict, \
        "The structure details must be a dictionary if you want to supply a constructor.";
  
  def fxConvertFromJSONString(oSelf, sbJSONData, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    if f0AssertTypes: f0AssertTypes({
      "sbJSONData": (sbJSONData, bytes),
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    try:
      xJSONData = json.loads(sbJSONData);
    except:
      raise oSelf.cJSONDataSyntaxException("%s does not contain valid JSON" % sDataNameInError);
    xData = oSelf.fxConvertFromJSONData(xJSONData, sDataNameInError, s0BasePath, dxInheritingValues);
    return xData;
    
  def fxConvertFromJSONData(oSelf, xJSONData, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    if f0AssertTypes: f0AssertTypes({
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    xData = fxConvertFromJSONData(oSelf.xStructureDetails, xJSONData, sDataNameInError, s0BasePath, dxInheritingValues);
    if oSelf.f0oConstructor:
      try:
        xData = oSelf.f0oConstructor(**xData);
      except Exception as oException:
        oPyCode = oSelf.f0oConstructor.__code__;
        oException.args = tuple(
          ["%s in %s line number %d" % (oException.args[0], oPyCode.co_filename, oPyCode.co_firstlineno)]
          + list(oException.args)[1:]
        );
        raise;
    return xData;
  
  def fsbConvertToJSON(oSelf, oData, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    if f0AssertTypes: f0AssertTypes({
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    xJSONData = oSelf.fxConvertToJSONData(oData, sDataNameInError, s0BasePath, dxInheritingValues);
    sJSONData = json.dumps(xJSONData, sort_keys = True, indent = 2).replace("\n", "\r\n"); # We're on Windows
    return bytes(sJSONData, "ascii", "strict");
  
  def fxConvertToJSONData(oSelf, oData, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    if f0AssertTypes: f0AssertTypes({
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    assert oSelf.f0oConstructor, \
        "This function is only intended to be used for objects";
    return fxConvertToJSONData(oSelf.xStructureDetails, oData, sDataNameInError, s0BasePath, dxInheritingValues);

from .fxConvertFromJSONData import fxConvertFromJSONData;
from .fxConvertToJSONData import fxConvertToJSONData;

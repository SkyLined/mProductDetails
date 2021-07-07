import json;

try:
  from mNotProvided import fAssertTypes as f0AssertTypes;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mNotProvided'":
    raise;
  f0AssertTypes = None;

class iObjectWithInheritingDataStructure(object):
  # The following MUST be defined by a subclass:
  oDataStructure = None; # Latest data structure
  dxInheritingValues = None; 
  toCompatibleDataStructures = tuple(); # All historical supported data structures, ordered from newest to oldest.
  
  @classmethod
  def foConstructFromJSONString(cClass, sbJSON, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    # dxInheritingValues needs to be updated with cClass.dxInheritingValues but this
    # will be done in a call to cClass.foConstructFromJSONData later
    if f0AssertTypes: f0AssertTypes({
      "sbJSON": (sbJSON, bytes),
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    try:
      xJSONData = json.loads(sbJSON);
    except:
      raise cJSONDataSyntaxException("%s does not contain valid JSON" % sDataNameInError);
    return cClass.foConstructFromJSONData(xJSONData, sDataNameInError, s0BasePath, dxInheritingValues);
  
  @classmethod
  def foConstructFromJSONData(cClass, xJSONData, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    dxInheritingValues = dxInheritingValues.copy();
    for sValueName in cClass.dxInheritingValues:
      if sValueName not in dxInheritingValues:
        dxInheritingValues[sValueName] = cClass.dxInheritingValues[sValueName];
    if f0AssertTypes: f0AssertTypes({
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    return fxConvertFromJSONData(
      xStructureDetails = (
        cClass.oDataStructure,
        cClass.toCompatibleDataStructures,
      ),
      xJSONData = xJSONData,
      sDataNameInError = sDataNameInError,
      s0BasePath = s0BasePath,
      dxInheritingValues = dxInheritingValues,
    );
  
  def fsbConvertToJSONString(oSelf, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    # dxInheritingValues needs to be updated with cClass.dxInheritingValues but this
    # will be done in a call to oSelf.fxConvertToJSONData later
    if f0AssertTypes: f0AssertTypes({
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    xJSONData = oSelf.fxConvertToJSONData(sDataNameInError, s0BasePath, dxInheritingValues);
    sJSON = json.dumps(xJSONData, sort_keys = True, indent = 2).replace("\n", "\r\n"); # We're on Windows
    return bytes(sJSON, "ascii", "strict");
  
  def fxConvertToJSONData(oSelf, sDataNameInError, s0BasePath = None, dxInheritingValues = {}):
    dxInheritingValues = dxInheritingValues.copy();
    for sValueName in oSelf.__class__.dxInheritingValues:
      if sValueName not in dxInheritingValues:
        dxInheritingValues[sValueName] = oSelf.__class__.dxInheritingValues[sValueName];
    if f0AssertTypes: f0AssertTypes({
      "sDataNameInError": (sDataNameInError, str),
      "s0BasePath": (s0BasePath, str, None),
      "dxInheritingValues": (dxInheritingValues, dict),
    });
    return fxConvertToJSONData(
      xStructureDetails = oSelf.__class__.oDataStructure,
      xData = oSelf,
      sDataNameInError = sDataNameInError,
      s0BasePath = s0BasePath,
      dxInheritingValues = dxInheritingValues,
    );

from .fxConvertFromJSONData import fxConvertFromJSONData;
from .fxConvertToJSONData import fxConvertToJSONData;
from .mExceptions import *;

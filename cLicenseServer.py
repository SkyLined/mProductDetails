import json;

try:
  from mNotProvided import fAssertType as f0AssertType, fAssertTypes as f0AssertTypes;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mNotProvided'":
    raise;
  f0AssertType = f0AssertTypes = None;

from .cDataStructure import cDataStructure;
from .cLicenseCheckResult import cLicenseCheckResult;
from .mExceptions import *;
# The rest of the imports are at the end to prevent import loops.

goJSONLicenseServerErrorResponseStructure = cDataStructure(
  { # Two options: a dictionary containing an error message...
    "sError": "string",
  }
);

class cLicenseServer(object):
  def __init__(oSelf, sbServerURL):
    if f0AssertType: f0AssertType("sbServerURL", sbServerURL, bytes);
    oSelf.sbServerURL = sbServerURL;
  
  def foGetLicenseCheckResult(oSelf, oLicense, bCheckOnly = False):
    sSystemId = fsGetSystemId();
    sbJSONData = fsbGetHTTPResponseData(
      sbURL = b"".join([
        oSelf.sbServerURL,
        b"/" if oSelf.sbServerURL[-1:] != b"/" else b"",
        b"License_dxCheck.php",
      ]),
      sb0PostData = bytes(json.dumps({
        "sLicenseBlock": str(oLicense.sbLicenseBlock, "utf-8", "strict"),
        "sSystemId": sSystemId,
        "bCheckOnly": bCheckOnly,
        "s0RequestedStructureVersion": cLicenseCheckResult.sRequestStructureVersion,
      }), "ascii", "strict"), 
      sURLNameInException = "The license server at " + str(oSelf.sbServerURL, "ascii", "strict"),
    );
    try:
      xJSONData = json.loads(sbJSONData);
    except:
      raise cJSONDataSyntaxException("%s does not contain valid JSON" % sDataNameInError);
    
    dsError_or_oLicenseCheckResult = fxConvertFromJSONData(
      xStructureDetails = (
        goJSONLicenseServerErrorResponseStructure,
        cLicenseCheckResult.oDataStructure,
        cLicenseCheckResult.toCompatibleDataStructures,
      ),
      xJSONData = xJSONData,
      sDataNameInError = "License sever %s response" % str(oSelf.sbServerURL, "ascii", "strict"),
      s0BasePath = None,
      dxInheritingValues = {},
    )
    if isinstance(dsError_or_oLicenseCheckResult, cLicenseCheckResult):
      return dsError_or_oLicenseCheckResult;
    # This is not a cLicenseCheckResult instance; it is a dict with a string in its "sError" element:
    raise cServerResponseException(
      dsError_or_oLicenseCheckResult["sError"],
      {
        "sbServerURL": oSelf.sbServerURL,
        "sSystemId": sSystemId,
        "sLicenseId": oLicense.sLicenseId,
        "sRequestedStructureVersion": cLicenseCheckResult.sRequestStructureVersion
      },
    );
  
  def foDownloadUpdatedLicense(oSelf, oLicense):
    sSource = "The license server at " + str(oSelf.sbServerURL, "ascii", "strict");
    sbLicenseBlock = fsbGetHTTPResponseData(
      b"".join([
        oSelf.sbServerURL,
        b"/" if oSelf.sbServerURL[-1:] != b"/" else b"",
        b"License_Download.php?sLicenseId=%s&sUsername=%s",
      ]) % (bytes(oLicense.sLicenseId, "ascii", "strict"), bytes(oLicense.sLicenseeName, "ascii", "strict")), 
      sURLNameInException = sSource,
    );
    aoLicenseBlock = cLicense.faoForLicenseBlocks(sbLicenseBlock, sSource);
    assert len(aoLicenseBlock) == 1, \
        "Expected 1 license in license block from server, got %d:\r\n%s" % (len(aoLicenseBlock), sbLicenseBlock);
    return aoLicenseBlock[0];

from .cLicense import cLicense;
from .fsbGetHTTPResponseData import fsbGetHTTPResponseData;
from .fsGetSystemId import fsGetSystemId;
from .fxConvertFromJSONData import fxConvertFromJSONData;
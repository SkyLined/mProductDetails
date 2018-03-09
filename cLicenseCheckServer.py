import hashlib, json;
from mWindowsAPI import oSystemInfo;

from .cErrorException import cErrorException;
# The rest of the imports are at the end to prevent import loops.

class cLicenseCheckServer(object):
  class cServerErrorException(cErrorException):
    pass;

  def __init__(oSelf, sServerURL):
    oSelf.sServerURL = sServerURL;
  
  def foGetRegisterLicenseCheckResult(oSelf, oLicense):
    return oSelf.__foGetServerResult({
      "sAction": "register",
      "sLicenseBlock": oLicense.sLicenseBlock,
    });
  
  def foGetLicenseCheckResult(oSelf, oLicense):
    # Generate a unique system id. We want this to be a value that is unique to this system, which the server can use
    # to track on how many machines the product is actived. However, the value should not leak any information about
    # the system to the server. Windows provides a unique machine id, but I do not know how this value is created, so
    # it may be based on information from this system that could be extracted. Hence the unique id is hashed to
    # obscure any such information:
    sSystemId = hashlib.sha256(oSystemInfo.sUniqueSystemId).hexdigest();
    return oSelf.__foGetServerResult({
      "sAction": "check",
      "sLicenseBlock": oLicense.sLicenseBlock,
      "sSystemId": sSystemId,
    });
  
  def __foGetServerResult(oSelf, dxData):
    sLicenseCheckResultJSONData = fsGetHTTPResponseData(
      sURL = oSelf.sServerURL,
      sPostData = json.dumps(dxData), 
      sURLNameInException = "The license check server",
      cException = cLicenseCheckServer.cServerErrorException,
    );
    oJSONServerResponeStructure = cDataStructure(
      (
        { # Two options: an error...
          "sError": "string",
        },
        cDataStructure(
          { # ... or a result.
            "bLicenseIsValid": "boolean",
            "sLicenseIsRevokedForReason": "string",
            "bLicenseInstancesExceeded": "boolean",
            "oNextCheckWithServerDate": "date",
          },
          cConstructor = cLicenseCheckResult,
        ),
      )
    );
    try:
      dsError_or_oLicenseCheckResult = oJSONServerResponeStructure.fxParseJSON(
        sJSONData = sLicenseCheckResultJSONData,
        sDataNameInError = "The license server response",
      );
    except cDataStructure.cJSONSyntaxErrorException, oSyntaxErrorException:
      raise cLicenseCheckServer.cServerErrorException(oSyntaxErrorException.sMessage);
    
    if dsError_or_oLicenseCheckResult.__class__ == cLicenseCheckResult:
      return dsError_or_oLicenseCheckResult;
    # This is not a cLicenseCheckResult instance; it is a dict with a string in its "sError" element:
    sError = dsError_or_oLicenseCheckResult["sError"];
    raise cLicenseCheckServer.cServerErrorException(sError);

from .cDataStructure import cDataStructure;
from .cDate import cDate;
from .cLicenseCheckResult import cLicenseCheckResult;
from .fsGetHTTPResponseData import fsGetHTTPResponseData;

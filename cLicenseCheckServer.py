import json;

from .cErrorException import cErrorException;
# The rest of the imports are at the end to prevent import loops.

class cLicenseCheckServer(object):
  class cServerErrorException(cErrorException):
    pass;

  def __init__(oSelf, sServerURL):
    oSelf.sServerURL = sServerURL;
  
  def foGetLicenseCheckResult(oSelf, oLicense):
    sLicenseCheckResultJSONData = fsGetHTTPResponseData(
      sURL = oSelf.sServerURL,
      sPostData = json.dumps({
        "sLicenseBlock": oLicense.sLicenseBlock,
        "sSystemId": fsGetSystemId(),
      }), 
      sURLNameInException = "The license check server at " + oSelf.sServerURL,
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
            "bInLicensePeriod": ("boolean", None),
            "sLicenseIsRevokedForReason": ("string", None),
            "bDeactivatedOnSystem": ("boolean", None),
            "bLicenseInstancesExceeded": ("boolean", None),
            "oNextCheckWithServerDate": ("date", None),
            "sError": None,
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
from .cLicenseCheckResult import cLicenseCheckResult;
from .fsGetHTTPResponseData import fsGetHTTPResponseData;
from .fsGetSystemId import fsGetSystemId;

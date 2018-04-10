import hashlib, json, os;
from mWindowsAPI import oSystemInfo;

from .cErrorException import cErrorException;
# The rest of the imports are at the end to prevent import loops.

# Generate a unique system id. We want this to be a value that is unique to this OS install and user account, so
# the server can use it to track on how many machines the product is actived by a user, as this may be limited by
# the license. However, the value should not leak any information about the machine or the user to the server.
# Windows provides a unique machine id and user name that we can use, but these must be procesed to obscure the
# information they qould otherwise convey. Hashing these values should practically guarantee a unique id that does
# not provide any information about the machine or the user to the server.
gsSystemId = hashlib.sha256(oSystemInfo.sUniqueSystemId + str(os.getenv("USERNAME"))).hexdigest();

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
        "sSystemId": gsSystemId,
      }), 
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
from .cDate import cDate;
from .cLicenseCheckResult import cLicenseCheckResult;
from .fsGetHTTPResponseData import fsGetHTTPResponseData;

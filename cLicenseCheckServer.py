from .cDataStructure import cDataStructure;
from .cDate import cDate;
from .cErrorException import cErrorException;
from .cLicenseCheckResult import cLicenseCheckResult;
from .fsGetHTTPResponseData import fsGetHTTPResponseData;

class cLicenseCheckServer(object):
  class cServerErrorException(cErrorException):
    pass;

  def __init__(oSelf, sServerURL):
    oSelf.sServerURL = sServerURL;
  
  def foGetLicenseCheckResult(oSelf, xUnused = None, sLicenseBlock = None, sProductName = None, sLicenseVersion = None):
    assert xUnused is None, \
        "You must call this function with named arguments!";
    assert sLicenseBlock, \
        "You must provide a value for sLicenseBlock";
    assert sProductName, \
        "You must provide a value for sProductName";
    assert sLicenseVersion, \
        "You must provide a value for sLicenseVersion";
    sPostData = json.dumps({
      "sLicenseBlock": sLicenseBlock,
      "sLicenseVersion": sLicenseVersion,
      "sProductName": sProductName,
    });
    sLicenseCheckResultJSONData = fsGetHTTPResponseData(
      sURL = oSelf.sServerURL,
      sPostData = sPostData, 
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
            "bLicenseIsRevoked": "boolean",
            "bLicenseInstancesExceeded": "boolean",
            "oNextCheckWithServerDate": "date",
          },
          cConstructor = cLicenseCheckResult,
        ),
      )
    );
    try:
      oLicenseCheckResult = oJSONServerResponeStructure.fxParseJSON(
        sJSONData = sLicenseCheckResultJSONData,
        sDataNameInError = "The license server response",
      );
    except cDataStructure.cJSONSyntaxErrorException, oSyntaxErrorException:
      raise cLicenseCheckServer.cServerErrorException(oSyntaxErrorException.sMessage);
    
    if not oLicenseCheckResult.__class__ == cLicenseCheckResult:
      # This is not a cLicenseCheckResult instance; it is a dict with a string in its "sError" element:
      raise cLicenseCheckServer.cServerErrorException(oLicenseCheckResult["sError"]);
    return oLicenseCheckResult;


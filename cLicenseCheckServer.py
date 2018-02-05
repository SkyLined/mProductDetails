import json, urllib;

from .cDataStructure import cDataStructure;
from .cDate import cDate;
from .cErrorException import cErrorException;
from .cLicenseCheckResult import cLicenseCheckResult;

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
    try:
      oHTTPRequest = urllib.urlopen(oSelf.sServerURL, sPostData);
    except Exception as oException:
      raise cLicenseCheckServer.cServerErrorException("The license server could not be contacted (error: %s)" % repr(oException));
    uStatusCode = oHTTPRequest.getcode();
    if uStatusCode == 404:
      raise cLicenseCheckServer.cServerErrorException("The license server url is invalid (HTTP %03d)." % uStatusCode);
    if uStatusCode > 500:
      raise cLicenseCheckServer.cServerErrorException("The license server provided an error code %03d." % uStatusCode);
    if uStatusCode != 200:
      raise cLicenseCheckServer.cServerErrorException("The license server provided an unexpected response code %03d." % uStatusCode);
    
    sLicenseCheckResultJSONData = oHTTPRequest.read();
    if not sLicenseCheckResultJSONData:
      raise cLicenseCheckServer.cServerErrorException("The license server response does not contain any data.");

    oJSONServerResponeStructure = cDataStructure(
      (
        { # Two options: an error...
          "sError": "date",
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
    except cDataStructure.cSyntaxErrorException, oSyntaxErrorException:
      raise cLicenseCheckServer.cServerErrorException(oSyntaxErrorException.sMessage);
    
    if not oLicenseCheckResult.__class__ == cLicenseCheckResult:
      # This is not a cLicenseCheckResult instance; it is a dict with a string in its "sError" element:
      raise cLicenseCheckServer.cServerErrorException(oLicenseCheckResult["sError"]);
    return oLicenseCheckResult;


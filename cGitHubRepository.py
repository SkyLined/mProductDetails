import urllib;

from .cErrorException import cErrorException;

class cGitHubRepository(object):
  class cGitHubServerErrorException(cErrorException):
    pass;
  
  sType = "GitHub";
  
  def __init__(oSelf, sUserName, sRepositoryName, sBranch, sType = None):
    assert sType in [None, "GitHub"], \
        "sType should not be specified - it's used by cProductDetails in its JSON file data structure to distinguish different repository types";
    oSelf.sUserName = sUserName;
    oSelf.sRepositoryName = sRepositoryName;
    oSelf.sBranch = sBranch;
    oSelf.sProductDetailsJSONURL = "https://raw.githubusercontent.com/%s/%s/%s/dxProductDetails.json" % \
      (sUserName, sRepositoryName, sBranch);
    oSelf.sLatestVersionURL = "https://github.com/%s/%s/archive/%s.zip" % (sUserName, sRepositoryName, sBranch);
  
  @property
  def sLatestProductDetailsJSONData(oSelf):
    try:
      oHTTPRequest = urllib.urlopen(oSelf.sProductDetailsJSONURL);
    except Exception as oException:
      raise cGitHubRepository.cGitHubServerErrorException("Connection to %s failed with error %s." % \
          (sProductDetailsJSONURL, str(oException)));
    uStatusCode = oHTTPRequest.getcode();
    if uStatusCode != 200:
      return cGitHubRepository.cGitHubServerErrorException("Request for %s returned HTTP %03d." % \
          (oSelf.sProductDetailsJSONURL, uStatusCode));
    return oHTTPRequest.read();

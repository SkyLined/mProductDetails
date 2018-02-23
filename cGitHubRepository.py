from .cErrorException import cErrorException;
from .fsGetHTTPResponseData import fsGetHTTPResponseData;

class cGitHubRepository(object):
  sType = "GitHub";
  
  class cGitHubServerErrorException(cErrorException):
    pass;
  
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
    return fsGetHTTPResponseData(
      sURL = oSelf.sProductDetailsJSONURL,
      sPostData = None, 
      cException = cGitHubRepository.cGitHubServerErrorException,
    );

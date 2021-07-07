from .cDataStructure import cDataStructure;
from .fsbGetHTTPResponseData import fsbGetHTTPResponseData;
from .iObjectWithInheritingDataStructure import iObjectWithInheritingDataStructure;
from .iRepository import iRepository;

class cGitHubRepository(iRepository, iObjectWithInheritingDataStructure):
  dxInheritingValues = {
    "sStructureVersion": "2021-07-02 11:16",
  };
  sType = "GitHub";
  
  def __init__(oSelf, sbUserName, sbRepositoryName, sbBranch):
    oSelf.sbUserName = sbUserName;
    oSelf.sbRepositoryName = sbRepositoryName;
    oSelf.sbBranch = sbBranch;
    oSelf.sb0RepositoryURL = b"https://github.com/%s/%s/tree/%s" % (sbUserName, sbRepositoryName, sbBranch);
    oSelf.sb0ProductDetailsJSONURL = b"https://raw.githubusercontent.com/%s/%s/%s/dxProductDetails.json" % \
      (sbUserName, sbRepositoryName, sbBranch);
    oSelf.sb0LatestVersionZipURL = b"https://github.com/%s/%s/archive/%s.zip" % (sbUserName, sbRepositoryName, sbBranch);

cGitHubRepository.oDataStructure = cDataStructure(
  {
    "sStructureVersion": "string:2021-07-02 11:16",
    "sType": "string:GitHub",
    "sbUserName": "ascii",
    "sbRepositoryName": "ascii", 
    "sbBranch": "ascii",
  },
  f0oConstructor = (
    lambda
      sStructureVersion, # not used
      sType, # Not used
      sbUserName,
      sbRepositoryName,
      sbBranch:
    cGitHubRepository(
      sbUserName,
      sbRepositoryName,
      sbBranch
    )
  ),
);
cGitHubRepository.toCompatibleDataStructures = (
  cDataStructure(
    # Last version before "sStructureVersion" was introduced:
    {
      "sType": "string:GitHub",
      "sUserName": "ascii",
      "sRepositoryName": "ascii", 
      "sBranch": "ascii",
    },
    f0oConstructor = (
      lambda
        sType, # Not used
        sUserName,
        sRepositoryName,
        sBranch:
      cGitHubRepository(
        sbUserName = sUserName,
        sbRepositoryName = sRepositoryName,
        sbBranch = sBranch,
      )
    ),
  ),
);

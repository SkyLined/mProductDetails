import os, sys;

from mDateTime import cDate;
# The rest of the imports are at the end to prevent import loops.

gsJSONFileName = "dxProductDetails.json";

# goProductDetailsDataStructure is defined at the end of the file because it must refer to cProductDetails

class cProductDetails(object):
  __doProductDetails_by_mModule = {}; # Maps loaded modules to product details.
  
  @staticmethod
  def foGetForModule(mProductModule):
    # Load and return product details for a specific module (if it has them).
    if mProductModule in cProductDetails.__doProductDetails_by_mModule:
      return cProductDetails.__doProductDetails_by_mModule[mProductModule];
    oProductDetails = None; 
    if hasattr(mProductModule, "__file__"): # This is not a built-in module
      sProductFolderPath = os.path.normpath(os.path.abspath(os.path.dirname(mProductModule.__file__)));
      oProductDetails = cProductDetails.foReadForFolderPath(sProductFolderPath);
    cProductDetails.__doProductDetails_by_mModule[mProductModule] = oProductDetails;
    return oProductDetails;
  
  @staticmethod
  def foReadForFolderPath(sProductFolderPath):
    # It appears that a module can be loaded multiple times from the same location. The same product details
    # can be reused for all of them:
    for oProductDetails in cProductDetails.__doProductDetails_by_mModule.values():
      if oProductDetails and oProductDetails.sInstallationFolderPath.lower() == sProductFolderPath.lower():
        return oProductDetails; # Reuse existing product details.
    
    # Load and return product details
    sJSONFilePath = os.path.join(sProductFolderPath, gsJSONFileName);
    if not os.path.isfile(sJSONFilePath): # This module has no product details JSON file.
      return None;
    oJSONFile = open(sJSONFilePath, "rb");
    try:
      sProductDetailsJSONData = oJSONFile.read();
    finally:
      oJSONFile.close();
    oProductDetails = cProductDetails.foFromJSONData(
      sProductDetailsJSONData = sProductDetailsJSONData,
      sDataNameInError = "product details JSON file %s" % sJSONFilePath,
      sBasePath = sProductFolderPath,
    );
    oProductDetails.sInstallationFolderPath = sProductFolderPath;
    return oProductDetails;
  
  @staticmethod
  def foFromJSONData(sProductDetailsJSONData, sDataNameInError, sBasePath = None):
    return goProductDetailsDataStructure.fxParseJSON(
      sJSONData = sProductDetailsJSONData,
      sDataNameInError = sDataNameInError,
      sBasePath = sBasePath,
    );
  
  def __init__(oSelf,
    sProductName,
    oProductVersion,
    sProductAuthor,
    sProductURL,
    oTrialPeriodDuration,
    sLicenseServerURL,
    oRepository,
    asDependentOnProductNames,
  ):
    oSelf.sProductName = sProductName;
    oSelf.oProductVersion = oProductVersion;
    oSelf.sProductAuthor = sProductAuthor;
    oSelf.sProductURL = sProductURL;
    oSelf.oTrialPeriodDuration = oTrialPeriodDuration;
    oSelf.sLicenseServerURL = sLicenseServerURL;
    oSelf.oRepository = oRepository;
    oSelf.asDependentOnProductNames = asDependentOnProductNames;
    oSelf.sInstallationFolderPath = None;
    
    oSelf.__oLicense = None;
    oSelf.__oLatestProductDetailsFromRepository = None;
    oSelf.__bCheckedWithServer = False;
  
  def __repr__(oSelf):
    return "<cProductDetails for %s version %s @%X>" % (oSelf.sProductName, oSelf.oProductVersion, id(oSelf));
  
  def fbWriteToInstallationFolderPath(oSelf):
    sProductDetailsJSONData = goProductDetailsDataStructure.fsStringify(
      oData = oSelf,
      sDataNameInError = "Product details",
      sBasePath = oSelf.sInstallationFolderPath,
    );
    sJSONFilePath = os.path.join(oSelf.sInstallationFolderPath, gsJSONFileName);
    try:
      oFile = open(sJSONFilePath, "wb");
    except:
      return False;
    try:
       oFile.write(sProductDetailsJSONData);
    finally:
      oFile.close();
    return True;
  
  @property
  def oLicense(oSelf):
    if oSelf.__oLicense is None:
      oSelf.__oLicense = foGetLicenseCollectionForAllLoadedProducts().foGetLicenseForProductDetails(oSelf);
    return oSelf.__oLicense;
  
  @property
  def bRequiresLicense(oSelf):
    return oSelf.sLicenseServerURL is not None;
  
  @property
  def bHasTrialPeriod(oSelf):
    return oSelf.oTrialPeriodDuration is not None;
  
  @property
  def oTrialPeriodEndDate(oSelf):
    if not oSelf.bHasTrialPeriod:
      return None;
    # Find out when the application was first run and when the trial period will end.
    oFirstRunDate = cLicenseRegistryCache.foGetOrSetFirstRunDate(oSelf.sProductName);
    return oFirstRunDate.foGetEndDateForDuration(oSelf.oTrialPeriodDuration);
  
  @property
  def bInTrialPeriod(oSelf):
    return oSelf.oTrialPeriodEndDate and not oSelf.oTrialPeriodEndDate.fbIsInThePast();
  
  @property
  def oLatestProductDetailsFromRepository(oSelf):
    if oSelf.__oLatestProductDetailsFromRepository is None:
      # Because the repository can contain a newer version of dxProductDetails.json with changed or added values,
      # getting the upstream details can fail. In this case we will want to return a non-True value. To prevent us
      # from trying to parse it again, we will use False to indicate we tried (None is used to indicate we haven't
      # attempted to parse it yet).
      oSelf.__oLatestProductDetailsFromRepository = False;
      try:
        oSelf.__oLatestProductDetailsFromRepository = cProductDetails.foFromJSONData(
          sProductDetailsJSONData = oSelf.oRepository.sLatestProductDetailsJSONData,
          sDataNameInError = "latest product details JSON file from repository",
        );
      except:
        pass;
    return oSelf.__oLatestProductDetailsFromRepository;

  @property
  def oLatestProductVersion(oSelf):
    return oSelf.oLatestProductDetailsFromRepository and oSelf.oLatestProductDetailsFromRepository.oProductVersion;
  
  @property
  def bVersionIsUpToDate(oSelf):
    return oSelf.oLatestProductVersion and oSelf.oProductVersion >= oSelf.oLatestProductVersion;
  
  @property
  def bVersionIsPreRelease(oSelf):
    return oSelf.oLatestProductVersion and oSelf.oProductVersion > oSelf.oLatestProductVersion;

from .cDataStructure import cDataStructure;
from .cGitHubRepository import cGitHubRepository;
goProductDetailsDataStructure = cDataStructure(
  {
    "sProductName": "string", 
    "oProductVersion": "version",
    "sProductAuthor": "string", 
    "sProductURL": "string", 
    "oTrialPeriodDuration": ("duration", None),
    "sLicenseServerURL": ("string", None),
    "oRepository": (
      cDataStructure(
        {
          "sType": "string:GitHub",
          "sUserName": "string",
          "sRepositoryName": "string", 
          "sBranch": "string"
        },
        cGitHubRepository,
      ),
      # There are currently no other options
    ),
    "asDependentOnProductNames": [
      "string",
    ],
  },
  cProductDetails,
);

from .cLicenseRegistryCache import cLicenseRegistryCache;
from .foGetLicenseCollectionForAllLoadedProducts import foGetLicenseCollectionForAllLoadedProducts;
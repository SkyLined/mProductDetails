import os;

from mDateTime import cDateDuration;
try:
  from mNotProvided import fAssertTypes as f0AssertTypes;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mNotProvided'":
    raise;
  f0AssertTypes = None;

from .cVersion import cVersion;
from .iObjectWithInheritingDataStructure import iObjectWithInheritingDataStructure;
# The rest of the imports are at the end to prevent import loops.

gsJSONFileName = "dxProductDetails.json";

# goProductDetailsDataStructure is defined at the end of the file because it must refer to cProductDetails

class cProductDetails(iObjectWithInheritingDataStructure):
  dxInheritingValues = {
    "sStructureVersion": "2021-07-02 11:16",
  };
  __do0ProductDetails_by_mModule = {}; # Maps loaded modules to product details.
  
  @staticmethod
  def fo0GetForModule(mProductModule):
    # Load and return product details for a specific module (if it has them).
    if mProductModule in cProductDetails.__do0ProductDetails_by_mModule:
      return cProductDetails.__do0ProductDetails_by_mModule[mProductModule];
    if hasattr(mProductModule, "__file__"): # This is not a built-in module
      sProductFolderPath = os.path.normpath(os.path.abspath(os.path.dirname(mProductModule.__file__)));
      o0ProductDetails = cProductDetails.fo0ReadForFolderPath(sProductFolderPath);
    else:
      o0ProductDetails = None; 
    cProductDetails.__do0ProductDetails_by_mModule[mProductModule] = o0ProductDetails;
    return o0ProductDetails;
  
  @staticmethod
  def fo0ReadForFolderPath(sProductFolderPath):
    # It appears that a module can be loaded multiple times from the same location. The same product details
    # can be reused for all of them:
    for oProductDetails in cProductDetails.__do0ProductDetails_by_mModule.values():
      if oProductDetails and oProductDetails.s0InstallationFolderPath.lower() == sProductFolderPath.lower():
        return oProductDetails; # Reuse existing product details.
    
    # Load and return product details
    sJSONFilePath = os.path.join(sProductFolderPath, gsJSONFileName);
    if not os.path.isfile(sJSONFilePath): # This module has no product details JSON file.
      return None;
    oJSONFile = open(sJSONFilePath, "rb");
    try:
      sbProductDetailsJSONData = oJSONFile.read();
    finally:
      oJSONFile.close();
    oProductDetails = cProductDetails.foConstructFromJSONString(
      sbJSON = sbProductDetailsJSONData,
      sDataNameInError = sJSONFilePath,
      s0BasePath = sProductFolderPath,
    );
    oProductDetails.s0InstallationFolderPath = sProductFolderPath;
    return oProductDetails;
  
  def __init__(oSelf,
    sProductName,
    oProductVersion,
    sProductAuthor,
    asProductTypes,
    s0PythonModuleName = None,
    a0sPythonApplicationNames = None,
    a0sJavaScriptModuleNames = None,
    a0sPHPModuleNames = None,
    sb0ProductURL = None,
    o0TrialPeriodDuration = None,
    sb0LicenseServerURL = None,
    o0Repository = None,
    a0sDependentOnProductNames = None,
    a0sReleaseAdditionalProductNames = None,
    a0sDebugAdditionalProductNames = None,
  ):
    if f0AssertTypes: f0AssertTypes({
      "sProductName": (sProductName, str),
      "oProductVersion": (oProductVersion, cVersion),
      "sProductAuthor": (sProductAuthor, str),
      "asProductTypes": (asProductTypes, [str]),
      "s0PythonModuleName": (s0PythonModuleName, str if "Python module" in asProductTypes else None),
      "a0sPythonApplicationNames": (a0sPythonApplicationNames, [str] if "Python application" in asProductTypes else None),
      "a0sJavaScriptModuleNames": (a0sJavaScriptModuleNames, [str] if "JavaScript module" in asProductTypes else None),
      "a0sPHPModuleNames": (a0sPHPModuleNames, [str]if "PHP module" in asProductTypes else None),
      "sb0ProductURL": (sb0ProductURL, bytes, None),
      "o0TrialPeriodDuration": (o0TrialPeriodDuration, cDateDuration, None),
      "sb0LicenseServerURL": (sb0LicenseServerURL, bytes, None),
      "o0Repository": (o0Repository, iRepository, None),
      "a0sDependentOnProductNames": (a0sDependentOnProductNames, [str], None),
      "a0sReleaseAdditionalProductNames": (a0sReleaseAdditionalProductNames, [str], None),
      "a0sDebugAdditionalProductNames": (a0sDebugAdditionalProductNames, [str], None),
    });
    oSelf.sProductName = sProductName;
    oSelf.oProductVersion = oProductVersion;
    oSelf.sProductAuthor = sProductAuthor;
    oSelf.asProductTypes = asProductTypes;
    oSelf.s0PythonModuleName = s0PythonModuleName;
    oSelf.a0sPythonApplicationNames = a0sPythonApplicationNames and sorted(a0sPythonApplicationNames);
    oSelf.a0sJavaScriptModuleNames = a0sJavaScriptModuleNames and sorted(a0sJavaScriptModuleNames)
    oSelf.a0sPHPModuleNames = a0sPHPModuleNames and sorted(a0sPHPModuleNames);
    oSelf.sb0ProductURL = sb0ProductURL;
    oSelf.o0TrialPeriodDuration = o0TrialPeriodDuration;
    oSelf.sb0LicenseServerURL = sb0LicenseServerURL;
    oSelf.o0Repository = o0Repository;
    oSelf.a0sDependentOnProductNames = a0sDependentOnProductNames and sorted(a0sDependentOnProductNames);
    oSelf.a0sReleaseAdditionalProductNames = a0sReleaseAdditionalProductNames and sorted(a0sReleaseAdditionalProductNames);
    oSelf.a0sDebugAdditionalProductNames = a0sDebugAdditionalProductNames and sorted(a0sDebugAdditionalProductNames);
    
    oSelf.s0InstallationFolderPath = None;
    oSelf.__o0License = None;
    oSelf.__o0LatestProductDetailsFromRepository = None;
    oSelf.__bCheckedWithServer = False;
  
  def __repr__(oSelf):
    return "<cProductDetails for %s version %s @%X>" % (oSelf.sProductName, oSelf.oProductVersion, id(oSelf));
  
  def fbWriteToInstallationFolderPath(oSelf):
    assert oSelf.s0InstallationFolderPath, \
        "Cannot write to installation folder because oSelf.s0InstallationFolderPath is None";
    sbProductDetailsJSONData = oSelf.fsbConvertToJSONString(
      sDataNameInError = "%s.dxProductDetails" % oSelf.sProductName,
      s0BasePath = oSelf.s0InstallationFolderPath,
    );
    sJSONFilePath = os.path.join(oSelf.s0InstallationFolderPath, gsJSONFileName);
    try:
      with open(sJSONFilePath, "wb") as oFile:
        oFile.write(sbProductDetailsJSONData);
    except Exception:
      raise; # I want to catch only exceptions specific to write errors.
      return False;
    return True;
  
  @property
  def o0License(oSelf):
    if oSelf.__o0License is None:
      oSelf.__o0License = foGetLicenseCollectionForAllLoadedProducts().fo0GetLicenseForProductDetails(oSelf);
    return oSelf.__o0License;
  
  @property
  def bRequiresLicense(oSelf):
    return oSelf.sb0LicenseServerURL is not None;
  
  @property
  def bHasTrialPeriod(oSelf):
    return oSelf.o0TrialPeriodDuration is not None;
  
  @property
  def o0TrialPeriodEndDate(oSelf):
    if not oSelf.bHasTrialPeriod:
      return None;
    # Find out when the application was first run and when the trial period will end.
    oFirstRunDate = cLicenseRegistryCache.foGetOrSetFirstRunDate(oSelf.sProductName);
    return oFirstRunDate.foGetEndDateForDuration(oSelf.o0TrialPeriodDuration);
  
  @property
  def bInTrialPeriod(oSelf):
    return oSelf.o0TrialPeriodEndDate and not oSelf.o0TrialPeriodEndDate.fbIsInThePast();
  
  def foGetLatestProductDetailsFromRepository(oSelf):
    assert oSelf.o0Repository is not None, \
        "Cannot get latest product details because the product does not have a repository";
    if oSelf.__o0LatestProductDetailsFromRepository is None:
      oSelf.__o0LatestProductDetailsFromRepository = oSelf.o0Repository.foGetLatestProductDetails();
    return oSelf.__o0LatestProductDetailsFromRepository;
  
  @property
  def oLatestProductVersion(oSelf):
    assert oSelf.__o0LatestProductDetailsFromRepository, \
        "You must call .foGetLatestProductDetailsFromRepository() first and it must not return None";
    return oSelf.__o0LatestProductDetailsFromRepository.oProductVersion;
  
  @property
  def bVersionIsUpToDate(oSelf):
    assert oSelf.__o0LatestProductDetailsFromRepository, \
        "You must call .foGetLatestProductDetailsFromRepository() first and it must not return None";
    return oSelf.oProductVersion >= oSelf.__o0LatestProductDetailsFromRepository.oProductVersion;
  
  @property
  def bVersionIsPreRelease(oSelf):
    assert oSelf.__o0LatestProductDetailsFromRepository, \
        "You must call .foGetLatestProductDetailsFromRepository() first and it must not return None";
    return oSelf.oProductVersion > oSelf.__o0LatestProductDetailsFromRepository.oProductVersion;

from .cDataStructure import cDataStructure;
from .cGitHubRepository import cGitHubRepository;
cProductDetails.oDataStructure = cDataStructure(
  {
    "sStructureVersion": "string:2021-07-02 11:16",
    # required
    "sProductName": "string", 
    "oProductVersion": "version",
    "sProductAuthor": "string", 
    "asProductTypes": ["string"],
    # optional
    "?s0PythonModuleName": ("string", None),
    "?a0sPythonApplicationNames": (["string"], None),
    "?a0sJavaScriptModuleNames": (["string"], None),
    "?a0sPHPModuleNames": (["string"], None),
    "?sb0ProductURL": ("ascii", None), 
    "?o0TrialPeriodDuration": ("duration", None),
    "?sb0LicenseServerURL": ("ascii", None),
    "?o0Repository": (cGitHubRepository.oDataStructure, None),
    "?a0sDependentOnProductNames": (["string"], None),
    "?a0sReleaseAdditionalProductNames": (["string"], None),
    "?a0sDebugAdditionalProductNames": (["string"], None),
  },
  f0oConstructor = (
    lambda
      sStructureVersion, # not used
      sProductName,
      oProductVersion,
      sProductAuthor,
      asProductTypes,
      s0PythonModuleName = None,
      a0sPythonApplicationNames = None,
      a0sJavaScriptModuleNames = None,
      a0sPHPModuleNames = None,
      sb0ProductURL = None,
      o0TrialPeriodDuration = None,
      sb0LicenseServerURL = None,
      o0Repository = None,
      a0sDependentOnProductNames = None,
      a0sReleaseAdditionalProductNames = None,
      a0sDebugAdditionalProductNames = None:
    cProductDetails(
      sProductName = sProductName,
      oProductVersion = oProductVersion,
      sProductAuthor = sProductAuthor,
      asProductTypes = asProductTypes,
      s0PythonModuleName = s0PythonModuleName,
      a0sPythonApplicationNames = a0sPythonApplicationNames,
      a0sJavaScriptModuleNames = a0sJavaScriptModuleNames,
      a0sPHPModuleNames = a0sPHPModuleNames,
      sb0ProductURL = sb0ProductURL,
      o0TrialPeriodDuration = o0TrialPeriodDuration,
      sb0LicenseServerURL = sb0LicenseServerURL,
      o0Repository = o0Repository,
      a0sDependentOnProductNames = a0sDependentOnProductNames,
      a0sReleaseAdditionalProductNames = a0sReleaseAdditionalProductNames,
      a0sDebugAdditionalProductNames = a0sDebugAdditionalProductNames,
    )
  ),
);
cProductDetails.toCompatibleDataStructures = (
  cDataStructure(
    # Last version before "sStructureVersion" was introduced:
    {
      # required
      "sProductName": "string", 
      "oProductVersion": "version",
      "sProductAuthor": "string", 
      "asProductTypes": ["string"],
      # optional
      "?sPythonModuleName": "string",
      "?asPythonApplicationNames": ["string"],
      "?asJavaScriptModuleNames": ["string"],
      "?asPHPModuleNames": ["string"],
      "?sProductURL": ("ascii", None), 
      "?oTrialPeriodDuration": ("duration", None),
      "?sLicenseServerURL": ("ascii", None),
      "?oRepository": (
        cGitHubRepository.oDataStructure,
        cGitHubRepository.toCompatibleDataStructures,
        None # No repository
      ),
      "?asDependentOnProductNames": (["string"], None),
      "?asOptionalProductNames": (["string"], None),
    },
    f0oConstructor = (
      lambda
        sProductName,
        oProductVersion,
        sProductAuthor,
        asProductTypes,
        sPythonModuleName = None,
        asPythonApplicationNames = None,
        asJavaScriptModuleNames = None,
        asPHPModuleNames = None,
        sProductURL = None,
        oTrialPeriodDuration = None,
        sLicenseServerURL = None,
        oRepository = None,
        asDependentOnProductNames = None,
        asOptionalProductNames = None:
      cProductDetails(
        sProductName = sProductName,
        oProductVersion = oProductVersion,
        sProductAuthor = sProductAuthor,
        asProductTypes = asProductTypes,
        s0PythonModuleName = sPythonModuleName,
        a0sPythonApplicationNames = asPythonApplicationNames or None,
        a0sJavaScriptModuleNames = asJavaScriptModuleNames or None,
        a0sPHPModuleNames = asPHPModuleNames or None,
        sb0ProductURL = sProductURL,
        o0TrialPeriodDuration = oTrialPeriodDuration,
        sb0LicenseServerURL = sLicenseServerURL,
        o0Repository = oRepository,
        a0sDependentOnProductNames = asDependentOnProductNames,
        a0sReleaseAdditionalProductNames = asOptionalProductNames,
        a0sDebugAdditionalProductNames = asOptionalProductNames,
      )
    ),
  ),
);

from .cLicenseRegistryCache import cLicenseRegistryCache;
from .foGetLicenseCollectionForAllLoadedProducts import foGetLicenseCollectionForAllLoadedProducts;
from .iRepository import iRepository;

import os;

# The imports are at the end to prevent import loops.

gsJSONFileName = "dxProductDetails.json";

# goProductDetailsDataStructure is defined at the end of the file because it must refer to cProductDetails

class cProductDetails(object):
  doProductDetails_by_sName = {}; # Stores information on all loaded products.
  @staticmethod
  def foGetForProductName(sProductName):
    oProductDetails = cProductDetails.doProductDetails_by_sName.get(sProductName);
    assert oProductDetails, \
        "No cProductDetails instance has been created for %s" % sProductName;
    return oProductDetails;
  @staticmethod
  def foReadForMainModule():
    import __main__;
    return cProductDetails.foReadForModule(__main__);
  @staticmethod
  def foReadForModule(mProductModule):
    sProductFolderPath = os.path.dirname(mProductModule.__file__);
    return cProductDetails.foReadForFolderPath(sProductFolderPath);
  @staticmethod
  def foReadForFolderPath(sProductFolderPath):
    sJSONFilePath = os.path.join(sProductFolderPath, gsJSONFileName);
    return cProductDetails.foReadForJSONFilePath(sJSONFilePath);
  @staticmethod
  def foReadForJSONFilePath(sJSONFilePath):
    oJSONFile = open(sJSONFilePath, "rb");
    try:
      sProductDetailsJSONData = oJSONFile.read();
    finally:
      oJSONFile.close();
    oProductDetails = cProductDetails.foFromJSONData(
      sProductDetailsJSONData = sProductDetailsJSONData,
      sDataNameInError = "product details JSON file %s" % sJSONFilePath,
      sBasePath = os.path.dirname(sJSONFilePath),
    );
    return oProductDetails;

  @staticmethod
  def faoGetAllLoadedProductDetails():
    return cProductDetails.doProductDetails_by_sName.values();
  
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
    sTrialPeriodDuration,
    sLicenseServerURL,
    oRepository,
    asDependentOnProductNames,
  ):
    assert sProductName not in oSelf.doProductDetails_by_sName, \
        "Product %s should not be created twice" % sProductName;
    oSelf.doProductDetails_by_sName[sProductName] = oSelf;
    oSelf.sProductName = sProductName;
    oSelf.oProductVersion = oProductVersion;
    oSelf.sTrialPeriodDuration = sTrialPeriodDuration;
    oSelf.sLicenseServerURL = sLicenseServerURL;
    oSelf.oRepository = oRepository;
    oSelf.asDependentOnProductNames = asDependentOnProductNames;
    
    oSelf.oLicenseCheckServer = cLicenseCheckServer(sLicenseServerURL);
    oSelf.__oLicenseCollection = None;
    oSelf.__oLicense = None;
    oSelf.__oLatestProductDetailsFromRepository = None;
    oSelf.__bCheckedWithServer = False;
  
  def fbWriteForFolderPath(oSelf, sFolderPath):
    return oSelf.fbWriteToJSONFilePath(os.path.join(sFolderPath, gsJSONFileName));
  def fbWriteToJSONFilePath(oSelf, sFilePath):
    sProductDetailsJSONData = goProductDetailsDataStructure.fsStringify(
      oData = oSelf,
      sDataNameInError = "Product details",
      sBasePath = os.path.dirname(sFilePath),
    );
    try:
      oFile = open(sFilePath, "wb");
    except:
      return False;
    try:
       oFile.write(sProductDetailsJSONData);
    finally:
      oFile.close();
    return True;
  
  @property
  def oLicenseCollection(oSelf):
    if oSelf.__oLicenseCollection is None:
      oSelf.__oLicenseCollection = cLicenseCollection.foForDefaultLicenseFile();
      oSelf.__oLicenseCollection.faoAddLicenses(
        aoLicenses = cLicenseCheckRegistry.faoReadLicensesFromRegistry(sProductName = oSelf.sProductName),
      );
    return oSelf.__oLicenseCollection;
  
  def __fCheckLicense(oSelf):
    if not oSelf.__bCheckedWithServer:
      oFirstRunDate = cLicenseCheckRegistry.foGetOrSetFirstRunDate(oSelf.sProductName);
      assert oFirstRunDate, \
          "Cannot write to the registry";
      oSelf.oLicenseCollection.fCheckWithRegistryOrServer(oSelf.oLicenseCheckServer);
  
  @property
  def oLicense(oSelf):
    if oSelf.__oLicense is None:
      oSelf.__oLicense = oSelf.oLicenseCollection.foGetLicenseForProductName(oSelf.sProductName);
    return oSelf.__oLicense;
  
  @property
  def bHasTrialPeriod(oSelf):
    return oSelf.sTrialPeriodDuration is not None;
  
  @property
  def oTrialPeriodEndDate(oSelf):
    oSelf.__fCheckLicense();
    if not oSelf.bHasTrialPeriod:
      return None;
    # Find out when the application was first run and when the trial period will end.
    oFirstRunDate = cLicenseCheckRegistry.foGetFirstRunDate(oSelf.sProductName);
    return oFirstRunDate.foEndDateForDuration(oSelf.sTrialPeriodDuration);
  
  @property
  def bInTrialPeriod(oSelf):
    return oSelf.oTrialPeriodEndDate and cDate.foNow() <= oSelf.oTrialPeriodEndDate;
  
  def fasGetLicenseWarnings(oSelf):
    asLicenseWarnings = [];
    for oProductDetails in oSelf.doProductDetails_by_sName.values():
      oProductDetails.__fCheckLicense();
      if oProductDetails.oLicense:
        # Warn if license will expire in one month.
        if cDate.foNow().foEndDateForDuration("1m") > oProductDetails.oLicense.oEndDate:
          asLicenseWarnings.append("Your license for %s with id %s will expire on %s." % \
              (oProductDetails.sProductName, oProductDetails.oLicense.sLicenseId, oProductDetails.oLicense.oEndDate));
      elif oProductDetails.bInTrialPeriod:
        # Warn if in trial period
        asLicenseWarnings.append("Your trial period for %s will end on %s." % \
            (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate));
    return asLicenseWarnings;
  
  def fasGetLicenseErrors(oSelf):
    asLicenseErrors = [];
    for oProductDetails in oSelf.doProductDetails_by_sName.values():
      for sDependentOnProductName in oProductDetails.asDependentOnProductNames:
        assert sDependentOnProductName in oSelf.doProductDetails_by_sName, \
            "%s depends on %s, but no cProductDetails instance has been created for it." % \
            (oProductDetails.sProductName, sDependentOnProductName);
      oProductDetails.__fCheckLicense();
      if not oProductDetails.oLicense and not oProductDetails.bInTrialPeriod:
        asLicenseErrors += oProductDetails.oLicenseCollection.fasGetErrors(oProductDetails.sProductName);
        if oProductDetails.bHasTrialPeriod and not oProductDetails.bInTrialPeriod:
          asLicenseErrors.append("Your trial period for %s expired on %s" % \
              (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate));
    return asLicenseErrors;
  
  @property
  def oLatestProductDetailsFromRepository(oSelf):
    if oSelf.__oLatestProductDetailsFromRepository is None:
      # In case checking throws an error, set the value to false so we don't try again:
      oSelf.__oLatestProductDetailsFromRepository = False;
      oSelf.__oLatestProductDetailsFromRepository = cProductDetails.foFromJSONData(
        sProductDetailsJSONData = oSelf.oRepository.sLatestProductDetailsJSONData,
        sDataNameInError = "latest product details JSON file from repository",
      );
    return oSelf.__oLatestProductDetailsFromRepository;

  @property
  def oLatestProductVersion(oSelf):
    return oSelf.oLatestProductDetailsFromRepository and oSelf.oLatestProductDetailsFromRepository.oProductVersion;
  
  @property
  def bVersionIsUpToDate(oSelf):
    oSelf.oLatestProductVersion and oSelf.oProductVersion >= oSelf.oLatestProductVersion;
  
  @property
  def bVersionIsPreRelease(oSelf):
    oSelf.oLatestProductVersion and oSelf.oProductVersion > oSelf.oLatestProductVersion;

from .cDataStructure import cDataStructure;
from .cGitHubRepository import cGitHubRepository;
goProductDetailsDataStructure = cDataStructure(
  {
    "sProductName": "string", 
    "oProductVersion": "version",
    "sTrialPeriodDuration": ("string", "-"),
    "sLicenseServerURL": "string",
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

from .cDate import cDate;
from .cLicense import cLicense;
from .cLicenseCheckRegistry import cLicenseCheckRegistry;
from .cLicenseCheckServer import cLicenseCheckServer;
from .cLicenseCollection import cLicenseCollection;

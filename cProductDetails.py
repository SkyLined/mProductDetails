import os;

from .cDataStructure import cDataStructure;
from .cDate import cDate;
from .cGitHubRepository import cGitHubRepository;
# The rest of the local imports are at the end to prevent import loops.

class cProductDetails(object):
  @staticmethod
  def foReadFromFolderPath(sFolderPath):
    return cProductDetails.foReadFromJSONFilePath(sFolderPath + r"\dxProductDetails.json");
  @staticmethod
  def foReadFromJSONFilePath(sFilePath):
    oFile = open(sFilePath, "rb");
    try:
      sProductDetailsJSONData = oFile.read();
    finally:
      oFile.close();
    return cProductDetails.foFromJSONData(
      sProductDetailsJSONData = sProductDetailsJSONData,
      sDataNameInError = "product details JSON file",
      sBasePath = os.path.dirname(sFilePath),
    );
  
  @staticmethod
  def foFromJSONData(sProductDetailsJSONData, sDataNameInError, sBasePath):
    oJSONFileDataStructure = cDataStructure(
      {
        "sProductName": "string", 
        "oProductVersion": "version",
        "bRequiresLicense": "boolean",
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
      },
      cProductDetails,
    );
    
    return oJSONFileDataStructure.fxParseJSON(
      sJSONData = sProductDetailsJSONData,
      sDataNameInError = sDataNameInError,
      sBasePath = sBasePath,
    );
  
  def __init__(oSelf, sProductName, oProductVersion, bRequiresLicense, sTrialPeriodDuration, sLicenseServerURL, oRepository):
    oSelf.sProductName = sProductName;
    oSelf.oProductVersion = oProductVersion;
    oSelf.bRequiresLicense = bRequiresLicense;
    oSelf.sTrialPeriodDuration = sTrialPeriodDuration;
    oSelf.sLicenseServerURL = sLicenseServerURL;
    oSelf.oRepository = oRepository;
    
    oSelf.oLicenseCheckServer = cLicenseCheckServer(sLicenseServerURL);
    oSelf.__oLicenseCollection = None;
    oSelf.__oLicense = None;
    oSelf.__oLatestProductDetailsFromRepository = None;
    oSelf.__bCheckedWithServer = False;
  
  @property
  def oLicenseCollection(oSelf):
    if oSelf.__oLicenseCollection is None:
      oSelf.__oLicenseCollection = cLicenseCheckRegistry.foLicenseCollectionFromRegistry(sProductName = oSelf.sProductName);
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
    oSelf.__fCheckLicense();
    asLicenseWarnings = [];
    if oSelf.bRequiresLicense:
      if oSelf.oLicense:
        # Warn if license will expire in one month.
        if cDate.foNow().foEndDateForDuration("1m") > oSelf.oLicense.oEndDate:
          asLicenseWarnings.append("Your license will expire on %s" % oProductDetails.oLicense.oEndDate);
      elif oSelf.bInTrialPeriod:
        # Warn if in trial period
        asLicenseWarnings.append("Your trial period will expire on %s" % oSelf.oTrialPeriodEndDate);
    return asLicenseWarnings;
  
  def fasGetLicenseErrors(oSelf):
    oSelf.__fCheckLicense();
    asLicenseErrors = [];
    if oSelf.bRequiresLicense and not oSelf.oLicense and not oSelf.bInTrialPeriod:
      asLicenseErrors += oSelf.oLicenseCollection.fasGetErrors(oSelf.sProductName);
      if oSelf.bHasTrialPeriod and not oSelf.bInTrialPeriod:
        asLicenseErrors.append("Your trial period expired on %s" % oSelf.oTrialPeriodEndDate);
    return asLicenseErrors;
  
  @property
  def oLatestProductDetailsFromRepository(oSelf):
    if oSelf.__oLatestProductDetailsFromRepository is None:
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
  def oLatestProductVersion(oSelf):
    oSelf.oLatestProductVersion and oSelf.oProductVersion > oSelf.oLatestProductVersion;

from .cLicenseCheckRegistry import cLicenseCheckRegistry;
from .cLicenseCheckServer import cLicenseCheckServer;
from .cLicenseCollection import cLicenseCollection;

from .cDataStructure import cDataStructure;
# The rest of the local imports are at the end to prevent import loops.
from .cVersion import cVersion;

class cLicenseConfiguration(object):
  @staticmethod
  def faoReadFromJSONFile(sFilePath):
    oFile = open(sFilePath, "rb");
    try:
      sOrderedLicenseConfigurationsJSONData = oFile.read();
    finally:
      oFile.close();
    
    oJSONFileDataStructure = cDataStructure(
      [
        cDataStructure(
          {
            "asProductNames": ["string"],
            "sLicenseVersion": "string",
            "sLicenseURL": "string",
            "sHashingAlgorithmName": "string",
            "uHashLength": "unsigned integer",
            "sSecretKey": "string",
            "dsUsageTypeDescription_by_sKeyword": {"*": "string"},
          },
          cConstructor = cLicenseConfiguration,
        ),
      ],
    );

    return oJSONFileDataStructure.fxParseJSON(
      sJSONData = sOrderedLicenseConfigurationsJSONData,
      sDataNameInError = "license configuration JSON file",
    );

  def __init__(oSelf,
    asProductNames,
    sLicenseVersion,
    sLicenseURL,
    sHashingAlgorithmName,
    uHashLength,
    sSecretKey,
    dsUsageTypeDescription_by_sKeyword,
  ):
    oSelf.asProductNames = asProductNames;
    oSelf.sLicenseVersion = sLicenseVersion;
    oSelf.sLicenseURL = sLicenseURL;
    oSelf.sHashingAlgorithmName = sHashingAlgorithmName;
    oSelf.uHashLength = uHashLength;
    oSelf.sSecretKey = sSecretKey;
    oSelf.dsUsageTypeDescription_by_sKeyword = dsUsageTypeDescription_by_sKeyword;
  
  def foCreateLicense(oSelf, asProductNames, sLicenseeName, sUsageTypeKeyWord, uLicensedInstances, oStartDate, oEndDate):
    sUsageTypeDescription = oSelf.dsUsageTypeDescription_by_sKeyword.get(sUsageTypeKeyWord);
    assert sUsageTypeDescription, \
        "Unknown usage type keyword %s" % sUsageTypeKeyWord;
    # Create some random number ot use as the license id.
    oLicense = cLicense(
      asProductNames = asProductNames,
      sLicenseeName = sLicenseeName,
      sUsageTypeDescription = sUsageTypeDescription,
      uLicensedInstances = uLicensedInstances,
      oStartDate = oStartDate,
      oEndDate = oEndDate,
      sLicenseId = str(cVersion.foNew()),
      sLicenseVersion = oSelf.sLicenseVersion,
      sLicenseURL = oSelf.sLicenseURL,
    );
    oLicense.fCreateLicenseBlock(oSelf.sHashingAlgorithmName, oSelf.uHashLength, oSelf.sSecretKey);
    return oLicense;

from .cLicense import cLicense;

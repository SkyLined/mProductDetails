import hashlib, hmac, re;

from .cDate import cDate;
from .cErrorException import cErrorException;
# The rest of the local imports are at the end to prevent import loops.
from mWindowsAPI.mRegistry import cRegistryHiveKey, cRegistryHiveKeyNamedValue;

gsLicenseBlockHeader = "This is a license key covering software created by SkyLined";

gdcHashingAlgorithm_by_sName = {
  "MD5": hashlib.md5,
  "SHA256": hashlib.sha256,
};

srCRLF = r"[\r\n]*";

grLicenseBlock = re.compile("".join([
  r"\.\-+ ", re.escape(gsLicenseBlockHeader), " \-+\.", srCRLF,
  r"(",
    r"(?:", r"\| .+ \|", srCRLF, ")+",
  r")",
  r"'\-+ Authentication ([0-9a-f]+) \-+'", srCRLF,
]));
grLicenseBlockDetailsLine = re.compile(r"\| +(.+?)\.*: (.+?)\. +\|");

class cLicense(object):
  class cSyntaxErrorException(cErrorException):
    pass;
  
  @staticmethod
  def faoForLicenseBlocks(sLicenseBlocks, sProductName = None):
    aoLicenses = [];
    for oLicenseBlockMatch in grLicenseBlock.finditer(sLicenseBlocks):
      sLicenseBlock = oLicenseBlockMatch.group(0);
      sLicenseBlockDetails = oLicenseBlockMatch.group(1);
      dsConstructorArgumentName_by_sExpectedDetailsValueName = {
        "Licensed product": "sProductName",
        "Licensee": "sLicenseeName",
        "Licensed usage type": "sUsageTypeDescription",
        "Licensed instances": "uLicensedInstances",
        "Valid from": "oStartDate",
        "Valid to": "oEndDate",
        "License id": "sLicenseId",
        "License version": "sLicenseVersion",
        "Full license details at": "sLicenseURL",
      };
      dxConstructorArguments = {
        "sLicenseBlock": sLicenseBlock,
      };
      for oLicenseBlockDetailsLineMatch in grLicenseBlockDetailsLine.finditer(sLicenseBlockDetails):
        (sDetailsValueName, sValue) = oLicenseBlockDetailsLineMatch.groups();
        if sDetailsValueName in dxConstructorArguments:
          raise cLicense.cSyntaxErrorException("The license contains multiple values for %s, which is not expected" % sDetailsValueName);
        sConstructorArgumentName = dsConstructorArgumentName_by_sExpectedDetailsValueName.get(sDetailsValueName);
        if not sConstructorArgumentName:
          raise cLicense.cSyntaxErrorException("The license contains a value %s=%s, which is not expected" % (sDetailsValueName, sValue));
        if sConstructorArgumentName[0] == "s":
          xValue = sValue;
        elif sConstructorArgumentName[0] == "u":
          xValue = long(sValue);
          
        else:
          assert sConstructorArgumentName[0] == "o" and sConstructorArgumentName.endswith("Date"), \
              "Unrecognized constructor argument type %s" % sConstructorArgumentName;
          xValue = cDate.foFromString(sValue);
          if xValue is None:
            raise cLicense.cSyntaxErrorException("The license contains an invalid value %s=%s, which is not a date" % (sDetailsValueName, sValue));
        dxConstructorArguments[sConstructorArgumentName] = xValue;
        del dsConstructorArgumentName_by_sExpectedDetailsValueName[sDetailsValueName];
      for sExpectedDetailsValueName in dsConstructorArgumentName_by_sExpectedDetailsValueName.keys():
        raise cLicense.cSyntaxErrorException("The license does not contain a value for %s, which is required" % sExpectedDetailsValueName);
      if sProductName is None or dxConstructorArguments["sProductName"] == sProductName:
        aoLicenses.append(cLicense(**dxConstructorArguments));
    return aoLicenses;
  
  def __init__(oSelf,
    sProductName,
    sLicenseeName,
    sUsageTypeDescription,
    uLicensedInstances,
    oStartDate,
    oEndDate,
    sLicenseId,
    sLicenseVersion,
    sLicenseURL,
    sLicenseBlock = None,
  ):
    assert "\\" not in sProductName, \
        "The product name contains a slash (\\), which is not allowed";
    oSelf.sProductName = sProductName;
    oSelf.sLicenseeName = sLicenseeName;
    oSelf.sUsageTypeDescription = sUsageTypeDescription;
    oSelf.uLicensedInstances = uLicensedInstances;
    oSelf.oStartDate = oStartDate;
    oSelf.oEndDate = oEndDate;
    oSelf.sLicenseId = sLicenseId;
    oSelf.sLicenseVersion = sLicenseVersion;
    oSelf.sLicenseURL = sLicenseURL;
    oSelf.sLicenseBlock = sLicenseBlock;
    
    oSelf.__oLicenseCheckRegistry = cLicenseCheckRegistry(oSelf);
    oSelf.__oLicenseCheckResult = None;
  
  def fCreateLicenseBlock(oSelf, sHashingAlgorithmName, uHashLength, sSecretKey):
    cHashingAlgorithm = gdcHashingAlgorithm_by_sName[sHashingAlgorithmName];
    asDetailsLines = [
      "Licensed product............: %s" % oSelf.sProductName,
      "Licensee....................: %s" % oSelf.sLicenseeName,
      "Licensed usage type.........: %s" % oSelf.sUsageTypeDescription,
      "Licensed instances..........: %d" % oSelf.uLicensedInstances,
      "Valid from..................: %s" % oSelf.oStartDate,
      "Valid to....................: %s" % oSelf.oEndDate,
      "License id..................: %s" % oSelf.sLicenseId,
      "License version.............: %s" % oSelf.sLicenseVersion,
      "Full license details at.....: %s" % oSelf.sLicenseURL,
    ];
    sSaltedKey = sSecretKey + oSelf.sLicenseId;
    sHMAC = hmac.new(
      sSaltedKey,
      "".join(asDetailsLines),
      cHashingAlgorithm
    ).hexdigest()[:uHashLength];
    
    uBlockWidth = max(76, *[len(s) for s in asDetailsLines]) + 4;
    oSelf.sLicenseBlock = "".join(["%s\r\n" % s for s in [
      ".%s." % (" %s " % gsLicenseBlockHeader).center(uBlockWidth - 2, "-"),
    ] + [
      "| %s |" % sLine.ljust(uBlockWidth - 4) for sLine in asDetailsLines
    ] + [
      "'%s'" % (" Authentication %s " % sHMAC).center(uBlockWidth - 2, "-"),
    ]]);
  
  @property
  def bIsActive(oSelf):
    oToday = cDate.foNow();
    return oSelf.oStartDate <= oToday and oSelf.oEndDate >= oToday;
  
  @property
  def bIsExpired(oSelf):
    oToday = cDate.foNow();
    return oSelf.oEndDate and oSelf.oEndDate < oToday;
  
  def fCheckWithRegistryOrServer(oSelf, oLicenseCheckServer):
    oSelf.__oLicenseCheckResult = None;
    oToday = cDate.foNow();
    oLicenseCheckResult = oSelf.__oLicenseCheckRegistry.foGetLicenseCheckResult();
    # If the reigstry has cached check data, see if it's outdated:
    if oLicenseCheckResult and oLicenseCheckResult.oNextCheckWithServerDate > oToday:
      # The cached check data is fresh; use it.
      oSelf.__oLicenseCheckResult = oLicenseCheckResult;
    else:
      oSelf.fCheckWithServer(oLicenseCheckServer);
  
  def fCheckWithServer(oSelf, oLicenseCheckServer, bWriteToRegistry = True):
    oSelf.__oLicenseCheckResult = None;
    # Set bWriteToRegistry to True to disable caching of check results in the registry (e.g. in a system that
    # is used to generate licenses, you do not want to cache them).
    oSelf.__oLicenseCheckResult = oLicenseCheckServer.foGetLicenseCheckResult(
      sLicenseBlock = oSelf.sLicenseBlock,
      sProductName = oSelf.sProductName,
      sLicenseVersion = oSelf.sLicenseVersion,
    );
    if bWriteToRegistry:
      assert oSelf.fbWriteCheckResultToRegistry(), \
          "Cannot write to registry";
  
  def fbWriteCheckResultToRegistry(oSelf):
    return oSelf.__oLicenseCheckRegistry.fbSetLicenseCheckResult(oSelf.__oLicenseCheckResult);

  def fbWriteToRegistry(oSelf):
    return (
      oSelf.__oLicenseCheckRegistry.fbSetLicenseCheckResult(oSelf.__oLicenseCheckResult)
      and oSelf.__oLicenseCheckRegistry.fbSetLicenseBlock(oSelf.sLicenseBlock)
    );
  
  @property
  def bIsValid(oSelf):
    assert oSelf.__oLicenseCheckResult, \
        "You need to call fCheckWithRegistryOrServer or fCheckWithServer successfully before reading bIsValid";
    return oSelf.__oLicenseCheckResult.bLicenseIsValid;
  
  @property
  def bIsRevoked(oSelf):
    assert oSelf.__oLicenseCheckResult, \
        "You need to call fCheckWithRegistryOrServer or fCheckWithServer successfully before reading bIsRevoked";
    return oSelf.__oLicenseCheckResult.bLicenseIsRevoked;
  
  @property
  def bLicenseInstancesExceeded(oSelf):
    assert oSelf.__oLicenseCheckResult, \
        "You need to call fCheckWithRegistryOrServer or fCheckWithServer successfully before reading bInstancesExceeded";
    return oSelf.__oLicenseCheckResult.bLicenseInstancesExceeded;

from .cLicenseCheckRegistry import cLicenseCheckRegistry;

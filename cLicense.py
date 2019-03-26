import hashlib, hmac, re;

from mDateTime import cDate, cDateDuration;
from .cErrorException import cErrorException;
from .fsToOxfordComma import fsToOxfordComma;
from .fasFromOxfordComma import fasFromOxfordComma;
# The rest of the imports are at the end to prevent import loops.

gsLicenseBlockHeader = "This is a license key covering software created by SkyLined";

gdcHashingAlgorithm_by_sName = {
  "MD5": hashlib.md5,
  "SHA256": hashlib.sha256,
};

srCRLF = r"[\r\n]+";
srOptionalCRLF = r"[\r\n]*";

grLicenseBlock = re.compile("".join([
  r"\.\-+ ", re.escape(gsLicenseBlockHeader), " \-+\.", srCRLF,
  r"(",
    r"(?:", r"\| [^\r\n]+ \|", srCRLF, ")+",
  r")",
  r"'\-+ License id: (\w{32}) \-+'", srOptionalCRLF,
]));
grLicenseBlockDetailsLine = re.compile(r"\| +(.+?)\.*: (.+?) +\|");
import __main__;

class cLicense(object):
  class cSyntaxErrorException(cErrorException):
    pass;
  
  @staticmethod
  def faoForLicenseBlocks(sLicenseBlocks):
    aoLicenses = [];
    for oLicenseBlockMatch in grLicenseBlock.finditer(sLicenseBlocks):
      sLicenseBlock = oLicenseBlockMatch.group(0);
      sLicenseBlockDetails = oLicenseBlockMatch.group(1);
      sLicenseId = oLicenseBlockMatch.group(2);
      dsConstructorArgumentName_by_sExpectedDetailsValueName = {
        "Licensed products": "asProductNames",
        "Licensee": "sLicenseeName",
        "Licensed usage type": "sUsageTypeDescription",
        "Licensed instances": "uLicensedInstances",
        "Valid from": "oStartDate",
        "Valid to": "oEndDate",
        "Full license details at": "sLicenseURL",
      };
      dxConstructorArguments = {
        "sLicenseBlock": sLicenseBlock,
        "sLicenseId": sLicenseId,
      };
      for oLicenseBlockDetailsLineMatch in grLicenseBlockDetailsLine.finditer(sLicenseBlockDetails):
        (sDetailsValueName, sValue) = oLicenseBlockDetailsLineMatch.groups();
        if sDetailsValueName in dxConstructorArguments:
          raise cLicense.cSyntaxErrorException("The license contains multiple values for %s, which is not expected" % sDetailsValueName);
        sConstructorArgumentName = dsConstructorArgumentName_by_sExpectedDetailsValueName.get(sDetailsValueName);
        if not sConstructorArgumentName and sDetailsValueName[-1] != "s":
          # This could be the singular form (e.g. "Licensed product"); see if the plural exists:
          sConstructorArgumentName = dsConstructorArgumentName_by_sExpectedDetailsValueName.get(sDetailsValueName + "s");
        if not sConstructorArgumentName:
          raise cLicense.cSyntaxErrorException("The license contains a value %s=%s, which is not expected" % (sDetailsValueName, sValue));
        if sConstructorArgumentName[0:2] == "as":
          xValue = fasFromOxfordComma(sValue);
        elif sConstructorArgumentName[0] == "s":
          xValue = sValue;
        elif sConstructorArgumentName[0] == "u":
          xValue = long(sValue);
        else:
          assert sConstructorArgumentName[0] == "o" and sConstructorArgumentName.endswith("Date"), \
              "Unrecognized constructor argument type %s" % sConstructorArgumentName;
          try:
            xValue = cDate.foFromString(sValue);
          except:
            raise cLicense.cSyntaxErrorException("The license contains an invalid value %s=%s, which is not a date" % (sDetailsValueName, sValue));
        dxConstructorArguments[sConstructorArgumentName] = xValue;
        del dsConstructorArgumentName_by_sExpectedDetailsValueName[sDetailsValueName];
      for sExpectedDetailsValueName in dsConstructorArgumentName_by_sExpectedDetailsValueName.keys():
        raise cLicense.cSyntaxErrorException("The license does not contain a value for %s, which is required" % sExpectedDetailsValueName);
      aoLicenses.append(cLicense(**dxConstructorArguments));
    return aoLicenses;
  
  def __init__(oSelf,
    asProductNames,
    sLicenseeName,
    sUsageTypeDescription,
    uLicensedInstances,
    oStartDate,
    oEndDate,
    sLicenseURL,
    sLicenseBlock,
    sLicenseId,
  ):
    oSelf.asProductNames = asProductNames;
    oSelf.sLicenseeName = sLicenseeName;
    oSelf.sUsageTypeDescription = sUsageTypeDescription;
    oSelf.uLicensedInstances = uLicensedInstances;
    oSelf.oStartDate = oStartDate;
    oSelf.oEndDate = oEndDate;
    oSelf.sLicenseURL = sLicenseURL;
    oSelf.sLicenseBlock = sLicenseBlock;
    oSelf.sLicenseId = sLicenseId;
    
    oSelf.__oLicenseRegistryCache = cLicenseRegistryCache(oSelf);
    oSelf.__oLicenseCheckResult = oSelf.__oLicenseRegistryCache.foGetLicenseCheckResult();
    oSelf.bNeedsToBeCheckedWithServer = (
      oSelf.__oLicenseCheckResult is None
      or not oSelf.__oLicenseCheckResult.oNextCheckWithServerDate.fbIsInTheFuture()
    );
    oSelf.sLicenseCheckServerError = None;
  
  @property
  def bIsActive(oSelf):
    return not oSelf.oStartDate.fbIsInTheFuture() and not oSelf.bIsExpired;
      
    return ;
  
  @property
  def bIsExpired(oSelf):
    return oSelf.oEndDate is not None and oSelf.oEndDate.fbIsInThePast();
  
  def fbRemoveFromRegistry(oSelf):
    return oSelf.__oLicenseRegistryCache.fbRemove();
  
  def fsCheckWithServerAndGetError(oSelf, oLicenseCheckServer, bForceCheck = False):
    # Set bWriteToRegistry to True to disable caching of check results in the registry (e.g. in a system that
    # is used to generate licenses, you do not want to cache them).
    if oSelf.bNeedsToBeCheckedWithServer or bForceCheck:
      oSelf.bNeedsToBeCheckedWithServer = False;
      try:
        oSelf.__oLicenseCheckResult = oLicenseCheckServer.foGetLicenseCheckResult(oSelf);
      except cLicenseCheckServer.cServerErrorException as oServerErrorException:
        oSelf.sLicenseCheckServerError = oServerErrorException.sMessage;
        return oServerErrorException.sMessage;
    if oSelf.__oLicenseCheckResult:
      assert oSelf.__oLicenseRegistryCache.fbSetLicenseCheckResult(oSelf.__oLicenseCheckResult), \
          "Cannot write to registry";
    return oSelf.sLicenseCheckServerError;
  
  def fbWriteToRegistry(oSelf):
    return oSelf.__oLicenseRegistryCache.fbSetLicenseBlock(oSelf.sLicenseBlock);
  
  @property
  def bIsValid(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bIsValid";
    return oSelf.__oLicenseCheckResult.bLicenseIsValid;
  
  @property
  def bMayNeedToBeUpdated(oSelf):
    return oSelf.__oLicenseCheckResult.bLicenseMayNeedToBeUpdated;
  
  @property
  def bInLicensePeriodAccordingToServer(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bInLicensePeriodAccordingToServer";
    return oSelf.__oLicenseCheckResult.bInLicensePeriod;
  
  @property
  def sIsRevokedForReason(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading sIsRevokedForReason";
    return oSelf.__oLicenseCheckResult.sLicenseIsRevokedForReason;
  
  @property
  def bDeactivatedOnSystem(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bDeactivatedOnSystem";
    return oSelf.__oLicenseCheckResult.bDeactivatedOnSystem;
  
  @property
  def bLicenseInstancesExceeded(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bLicenseInstancesExceeded";
    return oSelf.__oLicenseCheckResult.bLicenseInstancesExceeded;
  
  def fsGetError(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before calling fsGetError";
    if oSelf.sLicenseCheckServerError:
      return oSelf.sLicenseCheckServerError;
    elif oSelf.bIsExpired:
      return "License %s for %s expired on %s." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames), oSelf.oEndDate.fsToHumanReadableString());
    elif not oSelf.bIsActive:
      return "License %s for %s activates on %s." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames), oSelf.oStartDate.fsToHumanReadableString());
    elif not oSelf.bIsValid:
      return "License %s for %s is not valid." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames));
    elif not oSelf.bInLicensePeriodAccordingToServer:
      return "License %s for %s is not active at this date according to the server." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames));
    elif oSelf.sIsRevokedForReason:
      return "License %s for %s has been revoked: %s." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames), oSelf.sIsRevokedForReason);
    elif oSelf.bDeactivatedOnSystem:
      return "License %s for %s has been deactivated on this system." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames));
    elif oSelf.bLicenseInstancesExceeded:
      return "License %s for %s has exceeded its maximum number of instances." % \
          (oSelf.sLicenseId, fsToOxfordComma(oSelf.asProductNames));
    return None;

  def fasGetWarnings(oSelf):
    asLicenseWarnings = [];
    # warn if license will expire in less than one month.
    if cDate.foNow().foGetEndDateForDuration(cDateDuration.foFromString("1m")).fbIsAfter(oSelf.oEndDate):
      asLicenseWarnings.append("Your license for %s with id %s will expire on %s." % \
          (fsToOxfordComma(oSelf.asProductNames), oSelf.sLicenseId, oSelf.oEndDate.fsToHumanReadableString()));
    if oSelf.bMayNeedToBeUpdated:
      asLicenseWarnings.append("Your license for %s with id %s may need to be updated." % \
          (fsToOxfordComma(oSelf.asProductNames), oSelf.sLicenseId));
    return asLicenseWarnings;

from .cLicenseCheckServer import cLicenseCheckServer;
from .cLicenseRegistryCache import cLicenseRegistryCache;
from mWindowsAPI.mRegistry import cRegistryHiveKey, cRegistryHiveKeyNamedValue;

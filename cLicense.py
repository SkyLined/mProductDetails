import hashlib, re;

from mDateTime import cDate, cDateDuration;
from mHumanReadable import fsArrayToHumanReadableString, fasHumanReadableStringToArray;

# The rest of the imports are at the end to prevent import loops.

gsbLicenseBlockHeader = b"This is a license key covering software created by SkyLined";
srbCRLF = rb"[\r\n]+";
srbOptionalCRLF = rb"[\r\n]*";

grbLicenseBlock = re.compile(rb"".join([
  rb"\.\-+ ", re.escape(gsbLicenseBlockHeader), rb" \-+\.", srbCRLF,
  rb"(",
    rb"(?:", rb"\| [^\r\n]+ \|", srbCRLF, rb")+",
  rb")",
  rb"'\-+ License id: (\w{32}) \-+'", srbOptionalCRLF,
]));
grbLicenseBlockDetailsLine = re.compile(rb"\| (?:(.+?)\.*:|\s+) (.+?) +\|");
import __main__;

class cLicense(object):
  @staticmethod
  def faoForLicenseBlocks(sbLicenseBlocks, sBlocksSource):
    assert isinstance(sbLicenseBlocks, bytes), \
        "sbLicenseBlocks must be 'bytes', not %s (%s)" % (type(sbLicenseBlocks), repr(sbLicenseBlocks));
    aoLicenses = [];
    uBlockIndex = 0;
    for oLicenseBlockMatch in grbLicenseBlock.finditer(sbLicenseBlocks):
      uBlockIndex += 1;
      sbLicenseBlock = oLicenseBlockMatch.group(0);
      sbLicenseBlockDetails = oLicenseBlockMatch.group(1);
      sbLicenseId = oLicenseBlockMatch.group(2);
      dsConstructorArgumentName_by_sbExpectedDetailsValueName = {
        b"Licensed products": "asProductNames",
        b"Licensee": "sLicenseeName",
        b"Licensed usage type": "sUsageTypeDescription",
        b"Licensed instances": "uLicensedInstances",
        b"Valid from": "oStartDate",
        b"Valid to": "oEndDate",
        b"Full license details at": "sLicenseURL",
      };
      dxConstructorArguments = {
        "sbLicenseBlock": sbLicenseBlock,
        "sLicenseId": str(sbLicenseId, "ascii", "strict"),
        "sLicenseSource": "block #%d in %s" % (uBlockIndex, sBlocksSource),
      };
      s0PreviousConstructorArgumentName = None;
      for oLicenseBlockDetailsLineMatch in grbLicenseBlockDetailsLine.finditer(sbLicenseBlockDetails):
        (sb0DetailsValueName, sbValue) = oLicenseBlockDetailsLineMatch.groups();
        if sb0DetailsValueName is None:
          if s0PreviousConstructorArgumentName is None:
            raise cLicenseSyntaxErrorException(
              "The license contains a nameless value on the first line (%s), which is not expected" % repr(sValue),
              {"sbLicenseBlockDetails": sbLicenseBlockDetails},
            );
          sConstructorArgumentName = s0PreviousConstructorArgumentName;
        else:
          if sb0DetailsValueName in dsConstructorArgumentName_by_sbExpectedDetailsValueName:
            sbDetailsValueName = sb0DetailsValueName;
          elif (sb0DetailsValueName + "s") in dsConstructorArgumentName_by_sbExpectedDetailsValueName:
            sbDetailsValueName = sb0DetailsValueName + "s";
          else:
            raise cLicenseSyntaxErrorException(
              "The license contains a value %s=%s, which is not expected" % (sb0DetailsValueName, sbValue),
              {"sbLicenseBlockDetails": sbLicenseBlockDetails},
            );
          sConstructorArgumentName = dsConstructorArgumentName_by_sbExpectedDetailsValueName.get(sbDetailsValueName);
          del dsConstructorArgumentName_by_sbExpectedDetailsValueName[sbDetailsValueName];
        if sConstructorArgumentName[0:2] == "as":
          xValue = fasHumanReadableStringToArray(str(sbValue, "utf-8", "strict"));
        elif sConstructorArgumentName[0] == "s":
          xValue = str(sbValue, "utf-8", "strict");
        elif sConstructorArgumentName[0] == "u":
          xValue = int(sbValue);
        else:
          assert sConstructorArgumentName[0] == "o" and sConstructorArgumentName.endswith("Date"), \
              "Unrecognized constructor argument type %s" % sConstructorArgumentName;
          try:
            xValue = cDate.foFromString(str(sbValue, "utf-8", "strict"));
          except:
            raise cLicenseSyntaxErrorException(
              "The license contains an invalid value %s=%s, which is not a date" % (sb0DetailsValueName, sbValue),
              {"sbLicenseBlockDetails": sbLicenseBlockDetails},
            );
        if sb0DetailsValueName is None:
          dxConstructorArguments[sConstructorArgumentName] += xValue;
        else:
          dxConstructorArguments[sConstructorArgumentName] = xValue;
        s0PreviousConstructorArgumentName = sConstructorArgumentName;
      for sbExpectedDetailsValueName in dsConstructorArgumentName_by_sbExpectedDetailsValueName.keys():
        raise cLicenseSyntaxErrorException(
          "The license does not contain a value for %s, which is required" % sbExpectedDetailsValueName,
          {"sbLicenseBlockDetails": sbLicenseBlockDetails},
        );
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
    sbLicenseBlock,
    sLicenseId,
    sLicenseSource,
  ):
    oSelf.asProductNames = asProductNames;
    oSelf.sLicenseeName = sLicenseeName;
    oSelf.sUsageTypeDescription = sUsageTypeDescription;
    oSelf.uLicensedInstances = uLicensedInstances;
    oSelf.oStartDate = oStartDate;
    oSelf.oEndDate = oEndDate;
    oSelf.sLicenseURL = sLicenseURL;
    oSelf.sbLicenseBlock = sbLicenseBlock;
    oSelf.sLicenseId = sLicenseId;
    oSelf.sLicenseSource = sLicenseSource;
    
    oSelf.__oLicenseRegistryCache = cLicenseRegistryCache(oSelf);
    oSelf.__o0LicenseCheckResult = oSelf.__oLicenseRegistryCache.fo0GetLicenseCheckResult();
    oSelf.bNeedsToBeCheckedWithServer = (
      oSelf.__o0LicenseCheckResult is None
      or not oSelf.__o0LicenseCheckResult.oNextCheckWithServerDate.fbIsInTheFuture()
    );
    oSelf.sLicenseServerError = None;
  
  @property
  def bIsActive(oSelf):
    return not oSelf.oStartDate.fbIsInTheFuture() and not oSelf.bIsExpired;
  
  @property
  def bIsExpired(oSelf):
    return oSelf.oEndDate is not None and oSelf.oEndDate.fbIsInThePast();
  
  def fsCheckWithServerAndGetError(oSelf, oLicenseServer, bForceCheck = False):
    # Set bWriteToRegistry to True to disable caching of check results in the registry (e.g. in a system that
    # is used to generate licenses, you do not want to cache them).
    if oSelf.bNeedsToBeCheckedWithServer or bForceCheck:
      try:
        oSelf.__o0LicenseCheckResult = oLicenseServer.foGetLicenseCheckResult(oSelf);
      except (cServerResponseException, cJSONDataSyntaxException) as oServerResponseException:
        oSelf.sLicenseServerError = oServerResponseException.sMessage;
        return oServerResponseException.sMessage;
      oSelf.bNeedsToBeCheckedWithServer = False;
    if oSelf.__o0LicenseCheckResult:
      assert oSelf.__oLicenseRegistryCache.fbSetLicenseCheckResult(oSelf.__o0LicenseCheckResult), \
          "Cannot write to registry";
    return oSelf.sLicenseServerError;
  
  def fbWriteToRegistry(oSelf):
    return oSelf.__oLicenseRegistryCache.fbSetLicenseBlock(oSelf.sbLicenseBlock);
  def fbRemoveFromRegistry(oSelf):
    return oSelf.__oLicenseRegistryCache.fbRemove();
  
  @property
  def bIsValid(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bIsValid";
    return not oSelf.__o0LicenseCheckResult.s0LicensesIsInvalidForReason;
  
  @property
  def s0LicensesIsInvalidForReason(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bIsValid";
    return oSelf.__o0LicenseCheckResult.s0LicensesIsInvalidForReason;
  
  @property
  def bMayNeedToBeUpdated(oSelf):
    return oSelf.__o0LicenseCheckResult and oSelf.__o0LicenseCheckResult.bLicenseMayNeedToBeUpdated;
  
  @property
  def bInLicensePeriodAccordingToServer(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bInLicensePeriodAccordingToServer";
    return oSelf.__o0LicenseCheckResult.b0InLicensePeriod is True;
  
  @property
  def sIsRevokedForReason(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading sIsRevokedForReason";
    return oSelf.__o0LicenseCheckResult.s0LicenseIsRevokedForReason;
  
  @property
  def bDeactivatedOnSystem(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bDeactivatedOnSystem";
    return oSelf.__o0LicenseCheckResult.b0DeactivatedOnSystem is True;
  
  @property
  def bLicenseInstancesExceeded(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before reading bLicenseInstancesExceeded";
    return oSelf.__o0LicenseCheckResult.b0LicenseInstancesExceeded is True;
  
  def fsGetError(oSelf):
    assert not oSelf.bNeedsToBeCheckedWithServer, \
        "You need to call fsCheckWithServerAndReturnErrors successfully before calling fsGetError";
    if oSelf.sLicenseServerError:
      return oSelf.sLicenseServerError;
    elif oSelf.s0LicensesIsInvalidForReason:
      return "License %s for %s is invalid: %s." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames), oSelf.s0LicensesIsInvalidForReason);
    elif oSelf.bIsExpired:
      return "License %s for %s expired on %s." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames), oSelf.oEndDate.fsToHumanReadableString());
    elif not oSelf.bIsActive:
      return "License %s for %s activates on %s." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames), oSelf.oStartDate.fsToHumanReadableString());
    elif not oSelf.bIsValid:
      return "License %s for %s is not valid." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames));
    elif not oSelf.bInLicensePeriodAccordingToServer:
      return "License %s for %s is not active at this date according to the server." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames));
    elif oSelf.sIsRevokedForReason:
      return "License %s for %s has been revoked: %s." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames), oSelf.sIsRevokedForReason);
    elif oSelf.bDeactivatedOnSystem:
      return "License %s for %s has been deactivated on this system." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames));
    elif oSelf.bLicenseInstancesExceeded:
      return "License %s for %s has exceeded its maximum number of instances." % \
          (oSelf.sLicenseId, fsArrayToHumanReadableString(oSelf.asProductNames));
    return None;
  
  def fasGetWarnings(oSelf):
    asLicenseWarnings = [];
    # warn if license will expire in less than one month.
    if cDate.foNow().foGetEndDateForDuration(cDateDuration.foFromString("1m")).fbIsAfter(oSelf.oEndDate):
      asLicenseWarnings.append("Your license for %s in %s with id %s will expire on %s." % \
          (fsArrayToHumanReadableString(oSelf.asProductNames), oSelf.sLicenseSource, oSelf.sLicenseId, oSelf.oEndDate.fsToHumanReadableString()));
    if oSelf.bMayNeedToBeUpdated:
      asLicenseWarnings.append("Your license for %s in %s with id %s may need to be updated." % \
          (fsArrayToHumanReadableString(oSelf.asProductNames), oSelf.sLicenseSource, oSelf.sLicenseId));
    return asLicenseWarnings;

from .cLicenseServer import cLicenseServer;
from .cLicenseRegistryCache import cLicenseRegistryCache;
from .mExceptions import *;

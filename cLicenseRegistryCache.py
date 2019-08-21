from mDateTime import cDate;
# The rest of the imports are at the end to prevent import loops.

gsProductLicensesKeyPath = "Software\SkyLined\Licenses";
gsProductFirstRunKeyPath = "Software\SkyLined\FirstRunDate";

# Optional TODO: cleanup the registry by removing cached data for expired certificates.

# Create some convenience functions for getting values:
def fsGetStringValue(oRegistryHiveKey, sValueName):
  oRegistryValue = oRegistryHiveKey.foGetNamedValue(sValueName);
  if oRegistryValue is None or oRegistryValue.sTypeName != "REG_SZ":
    return None;
  return oRegistryValue.xValue;
def fbGetBooleanValue(oRegistryHiveKey, sValueName):
  oRegistryValue = oRegistryHiveKey.foGetNamedValue(sValueName);
  if oRegistryValue is None or oRegistryValue.sTypeName != "REG_DWORD":
    return None;
  return {0: False, 1: True}[oRegistryValue.xValue];
def foGetDateValue(oRegistryHiveKey, sValueName):
  oRegistryValue = oRegistryHiveKey.foGetNamedValue(sValueName);
  if oRegistryValue is None or oRegistryValue.sTypeName != "REG_SZ":
    return None;
  return cDate.foFromString(oRegistryValue.xValue);
# Create some convenience functions for setting values:
def fbSetStringValue(oRegistryHiveKey, sValueName, sValue):
  bResult = oRegistryHiveKey.foSetNamedValue(
    sValueName = sValueName, 
    sTypeName = "REG_SZ",
    xValue = sValue,
  ) is not None;
  if not bResult:
    print "Cannot write %s = %s to registry" % (sValueName, repr(sValue));
  return bResult;
def fbSetBooleanValue(oRegistryHiveKey, sValueName, bValue):
  bResult = oRegistryHiveKey.foSetNamedValue(
    sValueName = sValueName,
    sTypeName = "REG_DWORD",
    xValue = bValue and 1 or 0,
  );
  if not bResult:
    print "Cannot write %s = %s to registry" % (sValueName, repr(bValue));
  return bResult;
def fbSetDateValue(oRegistryHiveKey, sValueName, oValue):
  bResult = oRegistryHiveKey.foSetNamedValue(
    sValueName = sValueName, 
    sTypeName = "REG_SZ",
    xValue = oValue.fsToString(),
  ) is not None;
  if not bResult:
    print "Cannot write %s = %s to registry" % (sValueName, repr(oValue));
  return bResult;

class cLicenseRegistryCache(object):
  @staticmethod
  def faoReadLicensesFromRegistry():
    oProductLicensesRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyName = gsProductLicensesKeyPath,
    );
    oProductLicensesRegistryHiveKey.fbCreate(); # Make sure this key exists.
    aoLoadedLicenses = [];
    # Each product has its own sub-key under the main registry key
    # Sanity check everything; discard anything that is not as it should be.
    for (sLicenseId, oLicenseRegistryHiveKey) in oProductLicensesRegistryHiveKey.doSubKey_by_sName.items():
      oLicenseBlockRegistryValue = oLicenseRegistryHiveKey.foGetNamedValue(sValueName = "sLicenseBlock");
      # Read the license block from the registry and parse it.
      if oLicenseBlockRegistryValue is not None and oLicenseBlockRegistryValue.sTypeName == "REG_SZ":
        sLicenseBlock = oLicenseBlockRegistryValue.xValue;
        aoLicenses = cLicense.faoForLicenseBlocks(sLicenseBlock);
        # The license block should have exactly one license and it should be for the license id it is stored under:
        if (
          len(aoLicenses) == 1
          and aoLicenses[0].sLicenseId == sLicenseId
        ):
          aoLoadedLicenses += aoLicenses;
    return aoLoadedLicenses;
  
  @staticmethod
  def foGetFirstRunDate(sProductName):
    oProductRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyName = gsProductFirstRunKeyPath,
    );
    return foGetDateValue(oProductRegistryHiveKey, sProductName);
  
  @staticmethod
  def foGetOrSetFirstRunDate(sProductName):
    oFirstRunDate = cLicenseRegistryCache.foGetFirstRunDate(sProductName);
    if not oFirstRunDate:
      oProductRegistryHiveKey = cRegistryHiveKey(
        sHiveName = "HKCU",
        sKeyName = gsProductFirstRunKeyPath,
      );
      oFirstRunDate = cDate.foNow();
      if not fbSetDateValue(oProductRegistryHiveKey, sProductName, oFirstRunDate):
        return None;
    return oFirstRunDate;
  
  def __init__(oSelf, oLicense):
    # Open the registry
    oSelf.__oRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyName = "%s\%s" % (gsProductLicensesKeyPath, oLicense.sLicenseId),
    );
  
  def foGetLicenseCheckResult(oSelf):
    # Read the values, return None if one is missing
    bLicenseIsValid = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseIsValid");
    if bLicenseIsValid is None:
      return None;
    bLicenseMayNeedToBeUpdated = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseMayNeedToBeUpdated");
    if bLicenseMayNeedToBeUpdated is None:
      bLicenseMayNeedToBeUpdated = True; # Apparently this is an older license that does not have this value.
    bInLicensePeriod = None;
    sLicenseIsRevokedForReason = None;
    bDeactivatedOnSystem = None;
    bLicenseInstancesExceeded = None;
    if bLicenseIsValid:
      bInLicensePeriod = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bInLicensePeriod");
      if bInLicensePeriod is None:
        return None;
      if bInLicensePeriod:
        sLicenseIsRevokedForReason = fsGetStringValue(oSelf.__oRegistryHiveKey, "sLicenseIsRevokedForReason");
        if sLicenseIsRevokedForReason is None:
          bDeactivatedOnSystem = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bDeactivatedOnSystem");
          if bDeactivatedOnSystem is None:
            return None;
          if not bDeactivatedOnSystem:
            bLicenseInstancesExceeded = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseInstancesExceeded");
            if bLicenseInstancesExceeded is None:
              return None;
    oNextCheckWithServerDate = foGetDateValue(oSelf.__oRegistryHiveKey, "oNextCheckWithServerDate");
    if oNextCheckWithServerDate is None:
      return None;
    
    return cLicenseCheckResult(
      bLicenseIsValid = bLicenseIsValid,
      bLicenseMayNeedToBeUpdated = bLicenseMayNeedToBeUpdated,
      bInLicensePeriod = bInLicensePeriod,
      sLicenseIsRevokedForReason = sLicenseIsRevokedForReason,
      bDeactivatedOnSystem = bDeactivatedOnSystem,
      bLicenseInstancesExceeded = bLicenseInstancesExceeded,
      oNextCheckWithServerDate = oNextCheckWithServerDate,
    );
  
  def fbSetLicenseBlock(oSelf, sLicenseBlock):
    return oSelf.__oRegistryHiveKey.foSetNamedValue(
      sValueName = "sLicenseBlock", 
      sTypeName = "REG_SZ",
      xValue = str(sLicenseBlock),
    ) is not None;
  
  def fbSetLicenseCheckResult(oSelf, oLicenseCheckResult):
    # Write the values, return False if one fails.
    if not fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseIsValid", oLicenseCheckResult.bLicenseIsValid):
      return False;
    if not fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseMayNeedToBeUpdated", oLicenseCheckResult.bLicenseMayNeedToBeUpdated):
      return False;
    if not oLicenseCheckResult.bLicenseIsValid:
      return True;
    if not fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bInLicensePeriod", oLicenseCheckResult.bInLicensePeriod):
      return False;
    if not oLicenseCheckResult.bInLicensePeriod:
      return True;
    if not fbSetStringValue(oSelf.__oRegistryHiveKey, "sLicenseIsRevokedForReason", oLicenseCheckResult.sLicenseIsRevokedForReason):
      return False;
    if oLicenseCheckResult.sLicenseIsRevokedForReason:
      return True;
    if not fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bDeactivatedOnSystem", oLicenseCheckResult.bDeactivatedOnSystem):
      return False;
    if oLicenseCheckResult.bDeactivatedOnSystem:
      return True;
    if not fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseInstancesExceeded", oLicenseCheckResult.bLicenseInstancesExceeded):
      return False;
    if oLicenseCheckResult.bLicenseInstancesExceeded:
      return True;
    if not fbSetDateValue(oSelf.__oRegistryHiveKey, "oNextCheckWithServerDate", oLicenseCheckResult.oNextCheckWithServerDate):
      return False;
    return True;
  
  def fbRemove(oSelf):
    return oSelf.__oRegistryHiveKey.fbDelete();
  
from .cLicense import cLicense;
from .cLicenseCheckResult import cLicenseCheckResult;
from mRegistry import cRegistryHiveKey, cRegistryHiveKeyNamedValue, cRegistryValue;

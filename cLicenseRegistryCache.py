from mDateTime import cDate;
# The rest of the imports are at the end to prevent import loops.

gsProductLicensesKeyPath = "Software\SkyLined\Licenses";
gsProductFirstRunKeyPath = "Software\SkyLined\FirstRunDate";

gbShowDebugOutput = False;
# Optional TODO: cleanup the registry by removing cached data for expired certificates.

# Create some convenience functions for getting values:
def fsGetStringValue(oRegistryHiveKey, sValueName):
  o0RegistryValue = oRegistryHiveKey.fo0GetValueForName(sValueName);
  if o0RegistryValue is None or o0RegistryValue.sTypeName != "REG_SZ":
    return None;
  return o0RegistryValue.xValue;
def fbGetBooleanValue(oRegistryHiveKey, sValueName):
  o0RegistryValue = oRegistryHiveKey.fo0GetValueForName(sValueName);
  if o0RegistryValue is None or o0RegistryValue.sTypeName != "REG_DWORD":
    return None;
  return {0: False, 1: True}[o0RegistryValue.xValue];
def foGetDateValue(oRegistryHiveKey, sValueName):
  o0RegistryValue = oRegistryHiveKey.fo0GetValueForName(sValueName);
  if o0RegistryValue is None or o0RegistryValue.sTypeName != "REG_SZ":
    return None;
  return cDate.foFromString(o0RegistryValue.xValue);
# Create some convenience functions for setting values:
def fSetStringValue(oRegistryHiveKey, sValueName, sValue):
  oRegistryHiveKey.foSetValueForName(
    sValueName = sValueName, 
    sTypeName = "REG_SZ",
    xValue = sValue,
  );
def fSetBooleanValue(oRegistryHiveKey, sValueName, bValue):
  oRegistryHiveKey.foSetValueForName(
    sValueName = sValueName,
    sTypeName = "REG_DWORD",
    xValue = bValue and 1 or 0,
  );
def fSetDateValue(oRegistryHiveKey, sValueName, oValue):
  oRegistryHiveKey.foSetValueForName(
    sValueName = sValueName, 
    sTypeName = "REG_SZ",
    xValue = oValue.fsToString(),
  );

class cLicenseRegistryCache(object):
  @staticmethod
  def faoReadLicensesFromRegistry():
    oProductLicensesRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyPath = gsProductLicensesKeyPath,
    );
    oProductLicensesRegistryHiveKey.fbCreate(); # Make sure this key exists.
    aoLoadedLicenses = [];
    # Each product has its own sub-key under the main registry key
    # Sanity check everything; discard anything that is not as it should be.
    for (sLicenseId, oLicenseRegistryHiveKey) in oProductLicensesRegistryHiveKey.doSubKey_by_sName.items():
      o0LicenseBlockRegistryNamedValue = oLicenseRegistryHiveKey.fo0GetNamedValue(sValueName = "sLicenseBlock");
      # Read the license block from the registry and parse it.
      if o0LicenseBlockRegistryNamedValue is not None:
        oLicenseBlockRegistryValue = o0LicenseBlockRegistryNamedValue.foGet();
        if oLicenseBlockRegistryValue.sTypeName == "REG_SZ":
          aoLicenses = cLicense.faoForLicenseBlocks(bytes(oLicenseBlockRegistryValue.xValue, "ascii", "strict"), "registry key %s" % o0LicenseBlockRegistryNamedValue.sFullPath);
        # The license block should have exactly one license and it should be for the license id it is stored under:
        if (
          len(aoLicenses) == 1
          and aoLicenses[0].sLicenseId == sLicenseId
        ):
          aoLoadedLicenses += aoLicenses;
      # Clean up old registry values that are no longer used.
      oLicenseRegistryHiveKey.fbDeleteValueForName("bLicenseIsValid");
      oLicenseRegistryHiveKey.fbDeleteValueForName("bLicenseMayNeedToBeUpdated");
      oLicenseRegistryHiveKey.fbDeleteValueForName("bInLicensePeriod");
      oLicenseRegistryHiveKey.fbDeleteValueForName("sLicenseIsRevokedForReason");
      oLicenseRegistryHiveKey.fbDeleteValueForName("bDeactivatedOnSystem");
      oLicenseRegistryHiveKey.fbDeleteValueForName("bLicenseInstancesExceeded");
      oLicenseRegistryHiveKey.fbDeleteValueForName("oNextCheckWithServerDate");
    return aoLoadedLicenses;
  
  @staticmethod
  def foGetFirstRunDate(sProductName):
    oProductRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyPath = gsProductFirstRunKeyPath,
    );
    return foGetDateValue(oProductRegistryHiveKey, sProductName);
  
  @staticmethod
  def foGetOrSetFirstRunDate(sProductName):
    oFirstRunDate = cLicenseRegistryCache.foGetFirstRunDate(sProductName);
    if not oFirstRunDate:
      oProductRegistryHiveKey = cRegistryHiveKey(
        sHiveName = "HKCU",
        sKeyPath = gsProductFirstRunKeyPath,
      );
      oFirstRunDate = cDate.foNow();
      fSetDateValue(oProductRegistryHiveKey, sProductName, oFirstRunDate);
    return oFirstRunDate;
  
  def __init__(oSelf, oLicense):
    # Open the registry
    oSelf.__oRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyPath = "%s\\%s" % (gsProductLicensesKeyPath, oLicense.sLicenseId),
    );
  
  def fo0GetLicenseCheckResult(oSelf):
    # Read the values, return None if one is missing
    s0LicensesCheckResult = fsGetStringValue(oSelf.__oRegistryHiveKey, "sLicensesCheckResult");
    if s0LicensesCheckResult is None:
      return None;
    return cLicenseCheckResult.foConstructFromJSONString(
      sbJSON = bytes(s0LicensesCheckResult, "ascii", "strict"),
      sDataNameInError = "%s\\sLicensesCheckResult" % oSelf.__oRegistryHiveKey.sFullPath
    );
  
  def fSetLicenseBlock(oSelf, sbLicenseBlock):
    return fSetStringValue(oSelf.__oRegistryHiveKey, "sLicenseBlock", str(sbLicenseBlock, "ascii", "strict"));
  
  def fSetLicenseCheckResult(oSelf, oLicenseCheckResult):
    sbJSON = oLicenseCheckResult.fsbConvertToJSONString("License check result");
    return fSetStringValue(oSelf.__oRegistryHiveKey, "sLicensesCheckResult", str(sbJSON, "ascii", "strict"));
  
  def fbRemove(oSelf, bThrowErrors = False):
    return oSelf.__oRegistryHiveKey.fbDelete(bThrowErrors = bThrowErrors);
  
from .cLicense import cLicense;
from .cLicenseCheckResult import cLicenseCheckResult;
from mRegistry import cRegistryHiveKey;

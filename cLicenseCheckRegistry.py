from .cDate import cDate;
# The rest of the local imports are at the end to prevent import loops.
from mWindowsAPI.mRegistry import cRegistryHiveKey, cRegistryHiveKeyNamedValue, cRegistryValue;

gsMainKeyPath = "Software\SkyLined";

# Optional TODO: cleanup the registry by removing cached data for expired certificates.

# Create some convenience functions for getting values:
def fbGetBooleanValue(oRegistryHiveKey, sValueName):
  oRegistryValue = oRegistryHiveKey.foGetNamedValue(sValueName);
  if oRegistryValue is None or oRegistryValue.sTypeName != "REG_DWORD":
    return None;
  return {0: False, 1: True}[oRegistryValue.xValue];
def foGetDateValue(oRegistryHiveKey, sValueName):
  oDateRegistryValue = oRegistryHiveKey.foGetNamedValue(sValueName);
  if oDateRegistryValue is None or oDateRegistryValue.sTypeName != "REG_SZ":
    return None;
  return cDate.foFromString(oDateRegistryValue.xValue);
# Create some convenience functions for setting values:
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
    xValue = str(oValue),
  ) is not None;
  if not bResult:
    print "Cannot write %s = %s to registry" % (sValueName, repr(bValue));
  return bResult;

class cLicenseCheckRegistry(object):
  @staticmethod
  def foLicenseCollectionFromRegistry(sProductName = None):
    oProductsRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyName = gsMainKeyPath,
    );
    if sProductName:
      asProductNames = [sProductName];
    else:
      # Each product has its own sub-key under the main registry key
      asProductNames = oProductsRegistryHiveKey.doSubKey_by_sName.keys();
    aoLoadedLicenses = [];
    for sProductName in asProductNames:
      # Enumerate licenses by id in the registry
      oProductLicensesRegistryHiveKey = oProductsRegistryHiveKey.foGetSubKey(r"%s\%s" % (sProductName, "Licenses"));
      if not oProductLicensesRegistryHiveKey.bExists:
        continue;
      # Sanity check everything; discard anything that is not as it should be.
      for (sLicensId, oLicenseRegistryHiveKey) in oProductLicensesRegistryHiveKey.doSubKey_by_sName.items():
        oLicenseBlockRegistryValue = oLicenseRegistryHiveKey.foGetNamedValue(sValueName = "sLicenseBlock");
        # Read the license block from the registry and parse it.
        if oLicenseBlockRegistryValue is not None and oLicenseBlockRegistryValue.sTypeName == "REG_SZ":
          sLicenseBlock = oLicenseBlockRegistryValue.xValue;
          aoLicenses = cLicense.faoForLicenseBlocks(sLicenseBlock);
          # The license block should have exactly one license and it should be for the right procuct and license is:
          if (
            len(aoLicenses) == 1
            and aoLicenses[0].sProductName == sProductName
            and aoLicenses[0].sLicenseId == sLicensId
          ):
            aoLoadedLicenses += aoLicenses;
    return cLicenseCollection(aoLoadedLicenses);
  
  @staticmethod
  def foGetFirstRunDate(sProductName):
    oProductRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyName = r"%s\%s" % (gsMainKeyPath, sProductName),
    );
    return foGetDateValue(oProductRegistryHiveKey, "oFirstRunDate");
  
  @staticmethod
  def foGetOrSetFirstRunDate(sProductName):
    oFirstRunDate = cLicenseCheckRegistry.foGetFirstRunDate(sProductName);
    if not oFirstRunDate:
      oProductRegistryHiveKey = cRegistryHiveKey(
        sHiveName = "HKCU",
        sKeyName = r"%s\%s" % (gsMainKeyPath, sProductName),
      );
      oFirstRunDate = cDate.foNow();
      if not fbSetDateValue(oProductRegistryHiveKey, "oFirstRunDate", oFirstRunDate):
        return None;
    return oFirstRunDate;
  
  def __init__(oSelf, oLicense):
    # Open the registry
    oSelf.__oRegistryHiveKey = cRegistryHiveKey(
      sHiveName = "HKCU",
      sKeyName = "Software\SkyLined\%s\Licenses\%s" % (oLicense.sProductName, oLicense.sLicenseId),
    );
  
  def foGetLicenseCheckResult(oSelf):
    # Read the values, return None if one is missing
    bLicenseIsValid = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseIsValid");
    if bLicenseIsValid is None:
      return None;
    bLicenseIsRevoked = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseIsRevoked");
    if bLicenseIsRevoked is None:
      return None;
    bLicenseInstancesExceeded = fbGetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseInstancesExceeded");
    if bLicenseInstancesExceeded is None:
      return None;
    oNextCheckWithServerDate = foGetDateValue(oSelf.__oRegistryHiveKey, "oNextCheckWithServerDate");
    if oNextCheckWithServerDate is None:
      return None;
    
    return cLicenseCheckResult(
      bLicenseIsValid = bLicenseIsValid,
      bLicenseIsRevoked = bLicenseIsRevoked,
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
    return (
      fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseIsValid", oLicenseCheckResult.bLicenseIsValid)
      and fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseIsRevoked", oLicenseCheckResult.bLicenseIsRevoked)
      and fbSetBooleanValue(oSelf.__oRegistryHiveKey, "bLicenseInstancesExceeded", oLicenseCheckResult.bLicenseInstancesExceeded)
      and fbSetDateValue(oSelf.__oRegistryHiveKey, "oNextCheckWithServerDate", oLicenseCheckResult.oNextCheckWithServerDate)
    );

from .cLicense import cLicense;
from .cLicenseCheckResult import cLicenseCheckResult;
from .cLicenseCollection import cLicenseCollection;

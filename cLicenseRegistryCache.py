from mDateTime import cDate;
# The rest of the imports are at the end to prevent import loops.

# The code originally used HKEY_CURRENT_USER to store data but this has changed
# to prefer using HKEY_LOCAL_MACHINE. We want the license to be accessible to
# processes running as a different user on this machine. e.g. BugId can run as
# SYSTEM when it's installed as the JIT debugger. A normal user doesn't have
# write access to that location though, so the code should write to both.

gsProductLicensesKeyPath = "Software\\SkyLined\\Licenses";
gsProductFirstRunKeyPath = "Software\\SkyLined\\FirstRunDate";

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
    if c0RegistryHiveKey is None:
      return [];
    doLoadedLicense_by_sId = {};
    # Each product has its own sub-key under the main registry key
    # Sanity check everything; discard anything that is not as it should be.
    for sHiveName in ("HKLM", "HKCU"):
      oProductLicensesRegistryHiveKey = c0RegistryHiveKey(
        sHiveName = sHiveName,
        sKeyPath = gsProductLicensesKeyPath,
      );
      if oProductLicensesRegistryHiveKey.bExists:
        for (sLicenseId, oLicenseRegistryHiveKey) in oProductLicensesRegistryHiveKey.doSubKey_by_sName.items():
          o0LicenseBlockRegistryNamedValue = oLicenseRegistryHiveKey.fo0GetNamedValue(sValueName = "sLicenseBlock");
          # Read the license block from the registry and parse it.
          if o0LicenseBlockRegistryNamedValue is not None:
            oLicenseBlockRegistryValue = o0LicenseBlockRegistryNamedValue.foGet();
            if oLicenseBlockRegistryValue.sTypeName == "REG_SZ":
              aoLicenses = cLicense.faoForLicenseBlocks(
                bytes(oLicenseBlockRegistryValue.xValue, "ascii", "strict"),
                "registry key %s" % o0LicenseBlockRegistryNamedValue.sFullPath,
              );
            # The license block should have exactly one license and it should be for the license id it is stored under:
            if (
              len(aoLicenses) == 1
              and aoLicenses[0].sLicenseId == sLicenseId
            ):
              oLicense = aoLicenses[0];
              # Check if the license is already loaded, which can happen if it
              # is stored in both HKLM and HKCU:
              if sLicenseId not in doLoadedLicense_by_sId:
                # Add the license to the loaded licenses
                doLoadedLicense_by_sId[sLicenseId] = oLicense;
                if sHiveName == "HKCU":
                  # If this license was loaded from HKCU, it apparently does
                  # not exist in HKLM, which we checked first.
                  # We will try to copy it to HKLM, so all users can access it.
                  # This may fail if the user does not have write access to
                  # HKLM. The user must run the application with elevated
                  # privileges for this to succeed.
                  try:
                    oLicense.fWriteToRegistry();
                  except PermissionError:
                    pass;
    return doLoadedLicense_by_sId.values();
  
  @staticmethod
  def foGetFirstRunDate(sProductName):
    if c0RegistryHiveKey is None:
      raise NotImplementedError();
    oProductRegistryHiveKey = c0RegistryHiveKey(
      sHiveName = "HKCU",
      sKeyPath = gsProductFirstRunKeyPath,
    );
    if oProductRegistryHiveKey.bExists:
      return foGetDateValue(oProductRegistryHiveKey, sProductName);
    return None;
  
  @staticmethod
  def foGetOrSetFirstRunDate(sProductName):
    if c0RegistryHiveKey is None:
      raise NotImplementedError();
    oFirstRunDate = cLicenseRegistryCache.foGetFirstRunDate(sProductName);
    if not oFirstRunDate:
      oProductRegistryHiveKey = c0RegistryHiveKey(
        sHiveName = "HKCU",
        sKeyPath = gsProductFirstRunKeyPath,
      );
      oFirstRunDate = cDate.foNow();
      fSetDateValue(oProductRegistryHiveKey, sProductName, oFirstRunDate);
    return oFirstRunDate;
  
  def __init__(oSelf, oLicense):
    if c0RegistryHiveKey is not None:
      # Open the registry
      oSelf.__oMachineRegistryHiveKey = c0RegistryHiveKey(
        sHiveName = "HKLM",
        sKeyPath = "%s\\%s" % (gsProductLicensesKeyPath, oLicense.sLicenseId),
      );
      oSelf.__oUserRegistryHiveKey = c0RegistryHiveKey(
        sHiveName = "HKCU",
        sKeyPath = "%s\\%s" % (gsProductLicensesKeyPath, oLicense.sLicenseId),
      );
  
  def fo0GetLicenseCheckResult(oSelf):
    if c0RegistryHiveKey is None:
      return None;
    # Read the values, return None if one is missing
    s0LicensesCheckResult = fsGetStringValue(oSelf.__oMachineRegistryHiveKey, "sLicensesCheckResult");
    if s0LicensesCheckResult is not None:
      sRegistryKeyPath = f"{oSelf.__oMachineRegistryHiveKey.sFullPath}\\sLicensesCheckResult";
    else:
      s0LicensesCheckResult = fsGetStringValue(oSelf.__oUserRegistryHiveKey, "sLicensesCheckResult");
      if s0LicensesCheckResult is None:
        return None;
      sRegistryKeyPath = f"{oSelf.__oUserRegistryHiveKey.sFullPath}\\sLicensesCheckResult";
    return cLicenseCheckResult.foConstructFromJSONString(
      sbJSON = bytes(s0LicensesCheckResult, "ascii", "strict"),
      sDataNameInError = sRegistryKeyPath,
    );
  
  def fSetLicenseBlock(oSelf, sbLicenseBlock):
    if c0RegistryHiveKey is None:
      return;
    try:
      fSetStringValue(oSelf.__oMachineRegistryHiveKey, "sLicenseBlock", str(sbLicenseBlock, "ascii", "strict"));
    except PermissionError:
      pass;
    fSetStringValue(oSelf.__oUserRegistryHiveKey, "sLicenseBlock", str(sbLicenseBlock, "ascii", "strict"));
  
  def fSetLicenseCheckResult(oSelf, oLicenseCheckResult):
    if c0RegistryHiveKey is None:
      return;
    sbJSON = oLicenseCheckResult.fsbConvertToJSONString("License check result");
    fSetStringValue(oSelf.__oUserRegistryHiveKey, "sLicensesCheckResult", str(sbJSON, "ascii", "strict"));
  
  def fbRemove(oSelf, bThrowErrors = False):
    if c0RegistryHiveKey is None:
      return True;
    bRemoved = True;
    for oRegistryHiveKey in (oSelf.__oMachineRegistryHiveKey, oSelf.__oUserRegistryHiveKey):
      try:
        if oRegistryHiveKey.bExists and not oRegistryHiveKey.fbDelete(bThrowErrors = bThrowErrors):
          bRemoved = False;
      except PermissionError:
        pass;
    return bRemoved;

from .cLicense import cLicense;
from .cLicenseCheckResult import cLicenseCheckResult;
try:
  from mRegistry import cRegistryHiveKey as c0RegistryHiveKey;
except ModuleNotFoundError:
  c0RegistryHiveKey = None;

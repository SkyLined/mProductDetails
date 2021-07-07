from mDateTime import cDate;

try:
  from mNotProvided import fAssertTypes as f0AssertTypes;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mNotProvided'":
    raise;
  f0AssertTypes = None;

from .cVersion import cVersion;
from .iObjectWithInheritingDataStructure import iObjectWithInheritingDataStructure;
from .cDataStructure import cDataStructure;

class cLicenseCheckResult(iObjectWithInheritingDataStructure):
  sRequestStructureVersion = "2021-07-02 11:16"; # Which structure version to ask the server to provide.
  dxInheritingValues = {
    "sStructureVersion": "2021-07-02 11:16",
  };
  def __init__(oSelf,
    s0LicensesIsInvalidForReason,
    oNextCheckWithServerDate,
    bLicenseMayNeedToBeUpdated,
    b0InLicensePeriod,
    s0LicenseIsRevokedForReason,
    b0DeactivatedOnSystem,
    b0LicenseInstancesExceeded,
  ):
    if f0AssertTypes: f0AssertTypes({
      "s0LicensesIsInvalidForReason": (s0LicensesIsInvalidForReason, str, None),
      "bLicenseMayNeedToBeUpdated": (bLicenseMayNeedToBeUpdated, bool),
      "b0InLicensePeriod": (b0InLicensePeriod, bool, None),
      "s0LicenseIsRevokedForReason": (s0LicenseIsRevokedForReason, str, None),
      "b0DeactivatedOnSystem": (b0DeactivatedOnSystem, bool, None),
      "b0LicenseInstancesExceeded": (b0LicenseInstancesExceeded, bool, None),
      "oNextCheckWithServerDate": (oNextCheckWithServerDate, cDate),
    });
    oSelf.s0LicensesIsInvalidForReason = s0LicensesIsInvalidForReason;
    oSelf.bLicenseMayNeedToBeUpdated = bLicenseMayNeedToBeUpdated;
    oSelf.b0InLicensePeriod = b0InLicensePeriod;
    oSelf.s0LicenseIsRevokedForReason = s0LicenseIsRevokedForReason;
    oSelf.b0DeactivatedOnSystem = b0DeactivatedOnSystem;
    oSelf.b0LicenseInstancesExceeded = b0LicenseInstancesExceeded;
    oSelf.oNextCheckWithServerDate = oNextCheckWithServerDate;

cLicenseCheckResult.oDataStructure = cDataStructure(
  {
    "sStructureVersion": "string:2021-07-02 11:16",
    # required
    "s0LicensesIsInvalidForReason": ("string", None),
    "oNextCheckWithServerDate": ("date"),
    "bLicenseMayNeedToBeUpdated": ("boolean", None),
    "b0InLicensePeriod": ("boolean", None),
    "s0LicenseIsRevokedForReason": ("string", None),
    "b0DeactivatedOnSystem": ("boolean", None),
    "b0LicenseInstancesExceeded": ("boolean", None),
    # optional
    "?sError": None, # Automatically added by server; ignored.
  },
  f0oConstructor = (
    lambda 
      sStructureVersion, # not used
      s0LicensesIsInvalidForReason,
      oNextCheckWithServerDate,
      bLicenseMayNeedToBeUpdated,
      b0InLicensePeriod,
      s0LicenseIsRevokedForReason,
      b0DeactivatedOnSystem,
      b0LicenseInstancesExceeded,
      sError = None: # optional, ignored
    cLicenseCheckResult(
      s0LicensesIsInvalidForReason = s0LicensesIsInvalidForReason,
      oNextCheckWithServerDate = oNextCheckWithServerDate,
      bLicenseMayNeedToBeUpdated = bLicenseMayNeedToBeUpdated,
      b0InLicensePeriod = b0InLicensePeriod,
      s0LicenseIsRevokedForReason = s0LicenseIsRevokedForReason,
      b0DeactivatedOnSystem = b0DeactivatedOnSystem,
      b0LicenseInstancesExceeded = b0LicenseInstancesExceeded,
    )
  ),
);
cLicenseCheckResult.toCompatibleDataStructures = tuple(); # No older datastructures are supported at this time.;

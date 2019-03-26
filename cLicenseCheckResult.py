class cLicenseCheckResult(object):
  def __init__(oSelf, xUnused = None,
    bLicenseIsValid = None,
    bLicenseMayNeedToBeUpdated = None,
    bInLicensePeriod = None,
    sLicenseIsRevokedForReason = None,
    bDeactivatedOnSystem = None,
    bLicenseInstancesExceeded = None,
    oNextCheckWithServerDate = None,
    sError = None, # Required for creation using cDataStructure in cLicenseCheckServer
  ):
    assert xUnused is None, \
        "You must call this function with named arguments!";
    assert sError is None, \
        "You must call this function without a value for sError!";
    
    assert oNextCheckWithServerDate is not None, \
        "You must provide a valid value for oNextCheckWithServerDate";

    if isinstance(sLicenseIsRevokedForReason, unicode):
      try:
        sLicenseIsRevokedForReason = str(sLicenseIsRevokedForReason);
      except:
        raise AssertionError(
          "You must provide an ASCII string value for sLicenseIsRevokedForReason, not %s" % repr(sLicenseIsRevokedForReason)
        );
    oSelf.bLicenseIsValid = bLicenseIsValid;
    oSelf.bLicenseMayNeedToBeUpdated = bLicenseMayNeedToBeUpdated;
    oSelf.bInLicensePeriod = bInLicensePeriod;
    oSelf.sLicenseIsRevokedForReason = sLicenseIsRevokedForReason;
    oSelf.bDeactivatedOnSystem = bDeactivatedOnSystem;
    oSelf.bLicenseInstancesExceeded = bLicenseInstancesExceeded;
    oSelf.oNextCheckWithServerDate = oNextCheckWithServerDate;
    
    # bLicenseIsValid
    assert isinstance(bLicenseIsValid, bool), \
        "You must provide a valid value for bLicenseIsValid";
    if not bLicenseIsValid:
      assert bInLicensePeriod is None, \
          "You cannot provide a value for bInLicensePeriod == %s when bLicenseIsValid == False" % repr(bInLicensePeriod);
      assert sLicenseIsRevokedForReason is None, \
          "You cannot provide a value for sLicenseIsRevokedForReason when bLicenseIsValid == False";
      assert bDeactivatedOnSystem is None, \
          "You cannot provide a value for bDeactivatedOnSystem when bLicenseIsValid == False";
      assert bLicenseInstancesExceeded is None, \
          "You cannot provide a value for bLicenseInstancesExceeded when bLicenseIsValid == False";
      assert bLicenseMayNeedToBeUpdated is not None, \
          "You must provide a value for bLicenseMayNeedToBeUpdated when bLicenseIsValid == False";
      return;
    # bInLicensePeriod
    assert isinstance(bInLicensePeriod, bool), \
        "You must provide a valid value for bInLicensePeriod";
    if not bInLicensePeriod:
      assert sLicenseIsRevokedForReason is None, \
          "You cannot provide a value for sLicenseIsRevokedForReason when bInLicensePeriod == False";
      assert bDeactivatedOnSystem is None, \
          "You cannot provide a value for bDeactivatedOnSystem when bInLicensePeriod == False";
      assert bLicenseInstancesExceeded is None, \
          "You cannot provide a value for bLicenseInstancesExceeded when bInLicensePeriod == False";
      return;
    # sLicenseIsRevokedForReason
    if sLicenseIsRevokedForReason is not None:
      assert isinstance(sLicenseIsRevokedForReason, str), \
          "You must provide a string value for sLicenseIsRevokedForReason, not %s" % repr(sLicenseIsRevokedForReason);
      assert bDeactivatedOnSystem is None, \
          "You cannot provide a value for bDeactivatedOnSystem when sLicenseIsRevokedForReason != None";
      assert bLicenseInstancesExceeded is None, \
          "You cannot provide a value for bLicenseInstancesExceeded when sLicenseIsRevokedForReason != None";
      return;
    # bDeactivatedOnSystem
    assert isinstance(bDeactivatedOnSystem, bool), \
        "You must provide a valid value for bDeactivatedOnSystem";
    if bDeactivatedOnSystem:
      assert bLicenseInstancesExceeded is None, \
          "You cannot provide a value for bLicenseInstancesExceeded when bDeactivatedOnSystem == True";
      return;
    
    # bLicenseInstancesExceeded
    assert isinstance(bLicenseInstancesExceeded, bool), \
        "You must provide a valid value for bLicenseInstancesExceeded";


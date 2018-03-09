from .cDate import cDate;

class cLicenseCheckResult(object):
  def __init__(oSelf, xUnused = None,
    bLicenseInstancesExceeded = None, 
    sLicenseIsRevokedForReason = None,
    bLicenseIsValid = None,
    oNextCheckWithServerDate = None,
  ):
    assert xUnused is None, \
        "You must call this function with named arguments!";
    assert bLicenseInstancesExceeded is not None, \
        "You must provide a value for bLicenseInstancesExceeded";
    assert isinstance(bLicenseInstancesExceeded, bool), \
        "You must provide a boolean value for bLicenseInstancesExceeded, not %s" % repr(bLicenseInstancesExceeded);
    assert sLicenseIsRevokedForReason is not None, \
        "You must provide a value for sLicenseIsRevokedForReason";
    if isinstance(sLicenseIsRevokedForReason, unicode):
      try:
        sLicenseIsRevokedForReason = str(sLicenseIsRevokedForReason);
      except:
        raise AssertionError(
          "You must provide an ASCII string value for sLicenseIsRevokedForReason, not %s" % repr(sLicenseIsRevokedForReason)
        );
    else:
      assert isinstance(sLicenseIsRevokedForReason, str), \
          "You must provide a string value for sLicenseIsRevokedForReason, not %s" % repr(sLicenseIsRevokedForReason);
    assert bLicenseIsValid is not None, \
        "You must provide a value for bLicenseIsValid";
    assert isinstance(bLicenseIsValid, bool), \
        "You must provide a boolean value for bLicenseIsValid, not %s" % repr(bLicenseIsValid);
    assert oNextCheckWithServerDate is not None, \
        "You must provide a value for oNextCheckWithServerDate";
    assert isinstance(oNextCheckWithServerDate, cDate), \
        "You must provide a date value for oNextCheckWithServerDate, not %s" % repr(oNextCheckWithServerDate);
    
    oSelf.bLicenseInstancesExceeded = bLicenseInstancesExceeded;
    oSelf.sLicenseIsRevokedForReason = sLicenseIsRevokedForReason;
    oSelf.bLicenseIsValid = bLicenseIsValid;
    oSelf.oNextCheckWithServerDate = oNextCheckWithServerDate;


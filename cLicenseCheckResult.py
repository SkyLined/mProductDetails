from .cDate import cDate;

class cLicenseCheckResult(object):
  def __init__(oSelf, xUnused = None,
    bLicenseInstancesExceeded = None, 
    bLicenseIsRevoked = None,
    bLicenseIsValid = None,
    oNextCheckWithServerDate = None,
  ):
    assert xUnused is None, \
        "You must call this function with named arguments!";
    assert bLicenseInstancesExceeded is not None, \
        "You must provide a value for bLicenseInstancesExceeded";
    assert isinstance(bLicenseInstancesExceeded, bool), \
        "You must provide a boolean value for bLicenseInstancesExceeded, not %s" % repr(bLicenseInstancesExceeded);
    assert bLicenseIsRevoked is not None, \
        "You must provide a value for bLicenseIsRevoked";
    assert isinstance(bLicenseIsRevoked, bool), \
        "You must provide a boolean value for bLicenseIsRevoked, not %s" % repr(bLicenseIsRevoked);
    assert bLicenseIsValid is not None, \
        "You must provide a value for bLicenseIsValid";
    assert isinstance(bLicenseIsValid, bool), \
        "You must provide a boolean value for bLicenseIsValid, not %s" % repr(bLicenseIsValid);
    assert oNextCheckWithServerDate is not None, \
        "You must provide a value for oNextCheckWithServerDate";
    assert isinstance(oNextCheckWithServerDate, cDate), \
        "You must provide a date value for oNextCheckWithServerDate, not %s" % repr(oNextCheckWithServerDate);
    
    oSelf.bLicenseInstancesExceeded = bLicenseInstancesExceeded;
    oSelf.bLicenseIsRevoked = bLicenseIsRevoked;
    oSelf.bLicenseIsValid = bLicenseIsValid;
    oSelf.oNextCheckWithServerDate = oNextCheckWithServerDate;


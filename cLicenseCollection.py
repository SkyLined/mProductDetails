from mDateTime import cDate, cDateDuration;

gbDebugOutput = False;

# The imports are at the end to prevent import loops.
class cLicenseCollection(object):
  # A license collection is a list of licenses which offers some convenience functions to import and export them, check
  # them with the Windows registry and/or a server, get a valid&active license for a product, or a list of errors that
  # explain why there is no valid&active license for a product.
  def __init__(oSelf, aoProductDetails, aoLicenses, asLoadErrors, asLoadWarnings):
    oSelf.aoProductDetails = aoProductDetails;
    oSelf.aoLicenses = aoLicenses;
    oSelf.asLoadErrors = asLoadErrors;
    oSelf.asLoadWarnings = asLoadWarnings;
    oSelf.__tasErrorsAndWarnings = None;
  
  def ftasGetLicenseErrorsAndWarnings(oSelf):
    if oSelf.__tasErrorsAndWarnings is not None:
      return oSelf.__tasErrorsAndWarnings;
    doProductDetails_by_sProductName = dict([
      (oProductDetails.sProductName, oProductDetails)
      for oProductDetails in oSelf.aoProductDetails
    ]);
    oLicenseCheckServer = cLicenseCheckServer(oProductDetails.sLicenseServerURL);
    asLicenseErrors = oSelf.asLoadErrors[:];
    asLicenseWarnings = oSelf.asLoadWarnings[:];
    for oProductDetails in oSelf.aoProductDetails:
      if gbDebugOutput: print "* Product: %s %X" % (oProductDetails.sProductName, id(oProductDetails));
      bFoundValidLicense = False;
      asProductLicenseErrors = [];
      asProductLicenseWarnings = [];
      for oLicense in oSelf.aoLicenses:
        if gbDebugOutput: print "  * License: %s %X" % (oLicense.sLicenseId, id(oLicense));
        if oProductDetails.sProductName not in oLicense.asProductNames:
          if gbDebugOutput: print "    - for products %s" % ", ".join(oLicense.asProductNames);
          continue;
        if oLicense.bNeedsToBeCheckedWithServer:
          if gbDebugOutput: print "    * Checking with server...";
          sLicenseCheckServerError = oLicense.fsCheckWithServerAndGetError(oLicenseCheckServer);
          if sLicenseCheckServerError:
            if gbDebugOutput: print "    - %s" % sLicenseCheckServerError;
            asProductLicenseErrors.append(sLicenseCheckServerError);
            continue;
        sLicenseError = oLicense.fsGetError();
        if sLicenseError:
          if gbDebugOutput: print "    - %s" % sLicenseError;
          asProductLicenseErrors.append(sLicenseError);
          continue;
        if gbDebugOutput: print "    + OK";
        # This license is valid
        bFoundValidLicense = True;
        # warn if license will expire in less than one month.
        if cDate.foNow().foGetEndDateForDuration(cDateDuration.foFromString("1m")).fbIsAfter(oLicense.oEndDate):
          asProductLicenseWarnings.append("Your license for %s with id %s will expire on %s." % \
              (oProductDetails.sProductName, oLicense.sLicenseId, oLicense.oEndDate.fsToHumanReadableString()));
      if not bFoundValidLicense:
        if asProductLicenseErrors:
          # No valid license found; report the errors for the licenses
          if oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod:
            # This product is in its trial period; report all license errors as warnings:
            asProductLicenseWarnings = asProductLicenseErrors + asProductLicenseWarnings;
            asProductLicenseErrors = [];
            asProductLicenseWarnings.append(
              "Could not validate the license for %s and your trial period will expire on %s" %
              (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate.fsToHumanReadableString())
            );
        elif not oProductDetails.bHasTrialPeriod:
          # No license found; report an error if the product has no trial period.
          asProductLicenseErrors.append(
            "You have no license for %s" % oProductDetails.sProductName
          );
        elif oProductDetails.bInTrialPeriod:
          # No license found; report a warning if in the trial period.
          asProductLicenseWarnings.append(
            "You have no license for %s and your trial period will expire on %s" %
            (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate.fsToHumanReadableString())
          );
        else:
          # No license found; report an error if the trial period has expired.
          asProductLicenseErrors.append(
            "You have no license for %s and your trial period expired on %s" %
            (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate.fsToHumanReadableString())
          );
        asLicenseErrors += asProductLicenseErrors;
        asLicenseWarnings += asProductLicenseWarnings;
    oSelf.__tasErrorsAndWarnings = (asLicenseErrors, asLicenseWarnings);
    return oSelf.__tasErrorsAndWarnings;
  
  def foGetLicenseForProductDetails(oSelf, oProductDetails):
    # Return a valid active license for the product or None.
    assert oProductDetails in oSelf.aoProductDetails, \
        "Product %s is not in the license collection!?" % oProductDetails.sProductName;
    if gbDebugOutput: print "* Product: %s %X" % (oProductDetails.sProductName, id(oProductDetails));
    for oLicense in oSelf.aoLicenses:
      if gbDebugOutput: print "  * License: %s %X" % (oLicense.sLicenseId, id(oLicense));
      if oProductDetails.sProductName not in oLicense.asProductNames:
        if gbDebugOutput: print "    - product %s" % (oProductDetails.sProductName);
        continue;
      oLicenseCheckServer = cLicenseCheckServer(oProductDetails.sLicenseServerURL);
      sLicenseCheckServerError = oLicense.fsCheckWithServerAndGetError(oLicenseCheckServer);
      if sLicenseCheckServerError:
        if gbDebugOutput: print "    - %s" % sLicenseCheckServerError;
        continue;
      sLicenseError = oLicense.fsGetError();
      if sLicenseError:
        if gbDebugOutput: print "    - %s" % sLicenseError;
        continue;
      if gbDebugOutput: print "    + OK";
      return oLicense;
    assert oProductDetails.bInTrialPeriod, \
        "You cannot have a product without a license that is not in its trial period and reach this code. " \
        "Did you forget to call ftasGetLicenseErrorsAndWarnings first or to terminate when it reported errors?";
    return None;
  
  @property
  def sLicenseBlocks(oSelf):
    return "\r\n".join([oLicense.sLicenseBlock for oLicense in oSelf.aoLicenses]);

from .cLicense import cLicense;
from .cLicenseCheckServer import cLicenseCheckServer;

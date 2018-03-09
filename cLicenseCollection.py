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
  
  def ftasGetLicenseErrorsAndWarnings(oSelf):
    doProductDetails_by_sProductName = dict([
      (oProductDetails.sProductName, oProductDetails)
      for oProductDetails in oSelf.aoProductDetails
    ]);
    doLicenseCheckServer_by_sProductName = dict([
      (oProductDetails.sProductName, cLicenseCheckServer(oProductDetails.sLicenseServerURL))
      for oProductDetails in oSelf.aoProductDetails
    ]);
    asLicenseErrors = oSelf.asLoadErrors[:];
    asLicenseWarnings = oSelf.asLoadWarnings[:];
    for oProductDetails in oSelf.aoProductDetails:
      print "* Product: %s" % oProductDetails.sProductName;
      oLicenseCheckServer = doLicenseCheckServer_by_sProductName.get(oProductDetails.sProductName);
      asProductLicenseErrors = [];
      asProductLicenseWarnings = [];
      for oLicense in oSelf.aoLicenses:
        if oLicense.sProductName != oProductDetails.sProductName:
          print "  - License: %s for %s" % (oLicense.sLicenseId, oLicense.sProductName);
          continue;
        if oLicense.bNeedsToBeCheckedWithServer:
          print "  + License: %s for %s" % (oLicense.sLicenseId, oLicense.sProductName);
          sLicenseCheckServerError = oLicense.fsCheckWithServerAndGetError(oLicenseCheckServer);
          if sLicenseCheckServerError:
            asProductLicenseErrors.append(sLicenseCheckServerError);
            continue;
        else:
          print "  * License: %s for %s" % (oLicense.sLicenseId, oLicense.sProductName);
        sLicenseError = oLicense.fsGetError();
        if sLicenseError:
          asProductLicenseErrors.append(sLicenseError);
          continue;
        # This license is valid; warn if license will expire in one month or less.
        if cDate.foNow().foEndDateForDuration("1m") > oLicense.oEndDate:
          asProductLicenseWarnings.append("Your license for %s with id %s will expire on %s." % \
              (oProductDetails.sProductName, oLicense.sLicenseId, oLicense.oEndDate));
        # Stop looking for a valid license since we found one
        break;
      else:
        if asProductLicenseErrors:
          # No valid license found; report the errors for the licenses
          if oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod:
            # This product is in its trial period; report all license errors as warnings:
            asProductLicenseWarnings = asProductLicenseErrors + asProductLicenseWarnings;
            asProductLicenseErrors = [];
        elif not oProductDetails.bHasTrialPeriod:
          # No license found; report an error if the product has no trial period.
          asProductLicenseErrors.append(
            "You have no license for %s" % oProductDetails.sProductName
          );
        elif oProductDetails.bInTrialPeriod:
          # No license found; report a warning if in the trial period.
          asProductLicenseWarnings.append(
            "You have no license for %s and your trial period will expire on %s" %
            (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate)
          );
        else:
          # No license found; report an error if the trial period has expired.
          asProductLicenseErrors.append(
            "You have no license for %s and your trial period expired on %s" %
            (oProductDetails.sProductName, oProductDetails.oTrialPeriodEndDate)
          );
        asLicenseErrors += asProductLicenseErrors;
        asLicenseWarnings += asProductLicenseWarnings;
    return (asLicenseErrors, asLicenseWarnings);
  
  def foGetLicenseForProductDetails(oSelf, oProductDetails):
    # Return a valid active license for the product or None.
    assert oProductDetails in oSelf.aoProductDetails, \
        "Product %s is not in the license collection!?" % oProductDetails.sProductName;
    for oLicense in oSelf.aoLicenses:
      if oLicense.sProductName == oProductDetails.sProductName and not oLicense.fsGetError():
        return oLicense;
    assert oProductDetails.bInTrialPeriod, \
        "You cannot have a product without a license that is not in its trial period and reach this code. " \
        "Did you forget to call ftasGetLicenseErrorsAndWarnings first or to terminate when it reported errors?";
    return None;
  
  @property
  def sLicenseBlocks(oSelf):
    return "\r\n".join([oLicense.sLicenseBlock for oLicense in oSelf.aoLicenses]);

from .cDate import cDate;
from .cLicense import cLicense;
from .cLicenseCheckServer import cLicenseCheckServer;

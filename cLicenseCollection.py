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
    asLicenseErrors = oSelf.asLoadErrors[:];
    asLicenseWarnings = oSelf.asLoadWarnings[:];
    doLicenseServer_by_sbURL = {};
    for oProductDetails in oSelf.aoProductDetails:
      if oProductDetails.sb0LicenseServerURL is None:
        continue; # No license required.
      oLicenseServer = doLicenseServer_by_sbURL.get(oProductDetails.sb0LicenseServerURL);
      if not oLicenseServer:
        oLicenseServer = doLicenseServer_by_sbURL[oProductDetails.sb0LicenseServerURL] = \
            cLicenseServer(oProductDetails.sb0LicenseServerURL);
      if gbDebugOutput: print("* Product: %s %X" % (oProductDetails.sProductName, id(oProductDetails)));
      bFoundValidLicense = False;
      asProductLicensesErrors = [];
      asProductLicensesWarnings = [];
      asValidLicenseWarnings = [];
      for oLicense in oSelf.aoLicenses:
        asProductLicenseWarnings = oLicense.fasGetWarnings();
        if asProductLicenseWarnings:
          # We may want to show warnings for invalid licenses if we cannot find a valid one.
          for sLicenseWarning in asProductLicenseWarnings:
            if gbDebugOutput: print("    ! %s" % sLicenseWarning);
          asProductLicensesWarnings.extend(asProductLicenseWarnings);
        if gbDebugOutput: print("  * License: %s %X" % (oLicense.sLicenseId, id(oLicense)));
        if oProductDetails.sProductName not in oLicense.asProductNames:
          if gbDebugOutput: print("    - for products %s" % ", ".join(oLicense.asProductNames));
          continue;
        if oLicense.bNeedsToBeCheckedWithServer:
          if gbDebugOutput: print("    * Checking with server...");
          sLicenseServerError = oLicense.fsCheckWithServerAndGetError(oLicenseServer);
          if sLicenseServerError:
            if gbDebugOutput: print("    - %s" % sLicenseServerError);
            asProductLicensesErrors.append(sLicenseServerError);
            continue;
        sLicenseError = oLicense.fsGetError();
        if sLicenseError:
          if gbDebugOutput: print("    - %s" % sLicenseError);
          asProductLicensesErrors.append(sLicenseError);
          continue;
        if gbDebugOutput: print("    + OK");
        # This license is valid
        bFoundValidLicense = True;
        if asLicenseWarnings: # We always want to show warnings for valid licenses.
          asLicenseWarnings += asProductLicenseWarnings;
      if not bFoundValidLicense:
        if asProductLicensesErrors:
          # No valid license found; report the errors for the licenses
          if oProductDetails.bHasTrialPeriod and oProductDetails.bInTrialPeriod:
            # This product is in its trial period; report all license errors as warnings:
            asProductLicensesWarnings = asProductLicensesErrors + asProductLicensesWarnings;
            asProductLicensesErrors = [];
            asProductLicensesWarnings.append(
              "Could not validate the license for %s and your trial period will expire on %s" %
              (oProductDetails.sProductName, oProductDetails.o0TrialPeriodEndDate.fsToHumanReadableString())
            );
        elif not oProductDetails.bHasTrialPeriod:
          # No license found; report an error if the product has no trial period.
          asProductLicensesErrors.append(
            "You have no license for %s" % oProductDetails.sProductName
          );
        elif oProductDetails.bInTrialPeriod:
          # No license found; report a warning if in the trial period.
          asProductLicensesWarnings.append(
            "You have no license for %s and your trial period will expire on %s" %
            (oProductDetails.sProductName, oProductDetails.o0TrialPeriodEndDate.fsToHumanReadableString())
          );
        else:
          # No license found; report an error if the trial period has expired.
          asProductLicensesErrors.append(
            "You have no license for %s and your trial period expired on %s" %
            (oProductDetails.sProductName, oProductDetails.o0TrialPeriodEndDate.fsToHumanReadableString())
          );
        asLicenseErrors += asProductLicensesErrors;
        asLicenseWarnings += asProductLicensesWarnings;
    oSelf.__tasErrorsAndWarnings = (asLicenseErrors, asLicenseWarnings);
    return oSelf.__tasErrorsAndWarnings;
  
  def fo0GetLicenseForProductDetails(oSelf, oProductDetails):
    # Return a valid active license for the product or None.
    assert oProductDetails in oSelf.aoProductDetails, \
        "Product %s is not in the license collection!?" % oProductDetails.sProductName;
    if gbDebugOutput: print("* Product: %s %X" % (oProductDetails.sProductName, id(oProductDetails)));
    for oLicense in oSelf.aoLicenses:
      if gbDebugOutput: print("  * License: %s %X" % (oLicense.sLicenseId, id(oLicense)));
      if oProductDetails.sProductName not in oLicense.asProductNames:
        if gbDebugOutput: print("    - product %s" % (oProductDetails.sProductName));
        continue;
      if oProductDetails.sb0LicenseServerURL:
        oLicenseServer = cLicenseServer(oProductDetails.sb0LicenseServerURL);
        sLicenseServerError = oLicense.fsCheckWithServerAndGetError(oLicenseServer);
        if sLicenseServerError:
          if gbDebugOutput: print("    - %s" % sLicenseServerError);
          continue;
        sLicenseError = oLicense.fsGetError();
        if sLicenseError:
          if gbDebugOutput: print("    - %s" % sLicenseError);
          continue;
        if gbDebugOutput: print("    + OK");
      else:
        if gbDebugOutput: print("    + OK (no license check server)");
      return oLicense;
# ...actually you can if want to know if the product has a license:
#    assert oProductDetails.bInTrialPeriod, \
#        "You cannot have a product without a license that is not in its trial period and reach this code. " \
#        "Did you forget to call ftasGetLicenseErrorsAndWarnings first or to terminate when it reported errors?";
    return None;
  
  @property
  def sbLicenseBlocks(oSelf):
    return b"\r\n".join([oLicense.sbLicenseBlock for oLicense in oSelf.aoLicenses]);

from .cLicenseServer import cLicenseServer;

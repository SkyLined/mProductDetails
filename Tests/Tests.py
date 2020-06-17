from fTestDependencies import fTestDependencies;
fTestDependencies();

from mDebugOutput import fEnableDebugOutputForClass, fEnableDebugOutputForModule, fTerminateWithException;
try:
  import os, sys;

  import mProductDetails;
  from mProductDetails.fsToOxfordComma import fsToOxfordComma;

  print "Unique system id: " + mProductDetails.fsGetSystemId();

  print "Product version information:";
  oMainProductDetails = mProductDetails.foGetProductDetailsForModule(mProductDetails);
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  # Change order to put main product at the front:
  aoProductDetails.remove(oMainProductDetails);
  aoProductDetails.insert(0, oMainProductDetails);
  for oProductDetails in aoProductDetails:
    print "+ \"%s\" version \"%s\" by \"%s\" installed in \"%s\"." % \
        (oProductDetails.sProductName, oProductDetails.oProductVersion, oProductDetails.sProductAuthor, oProductDetails.sInstallationFolderPath);
  print;

  print "Checking licenses for loaded software products:";
  oLicenseCollection = mProductDetails.foGetLicenseCollectionForAllLoadedProducts();
  (asErrors, asWarnings) = oLicenseCollection.ftasGetLicenseErrorsAndWarnings();
  if asErrors:
    print "Software license error%s:" % (len(asErrors) > 1 and "s" or "");
    for sError in asErrors:
      print "- " + sError;
    print;

  if asWarnings:
    print "Software license warning%s:" % (len(asWarnings) > 1 and "s" or "");
    for sWarning in asWarnings:
      print "* " + sWarning;
    print;

  print "Software license information in registry:";
  aoLicenses = mProductDetails.faoGetLicensesFromRegistry();
  if not aoLicenses:
    print "- No licenses loaded";
  for oLicense in aoLicenses:
    print "+ %s licensed to %s:" % (oLicense.asProductNames[0], oLicense.sLicenseeName);
    print "  Products   : %s" % fsToOxfordComma(oLicense.asProductNames);
    print "  Usage type : %s" % oLicense.sUsageTypeDescription;
    print "  Instances  : %s" % oLicense.uLicensedInstances;
    print "  End date   : %s" % oLicense.oEndDate.fsToHumanReadableString();
    print "  Id         : %s" % oLicense.sLicenseId;

except Exception as oException:
  fTerminateWithException(oException);
import os, sys;

# Augment the search path: pretend we are in the parent folder so we can load mProductDetails as a module:
sMainFolderPath = os.path.abspath(os.path.dirname(__file__));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sys.path = [sParentFolderPath] + sys.path;

import mProductDetails;
from fsToOxfordComma import fsToOxfordComma;

print "Unique system id: " + mProductDetails.fsGetSystemId();

print "Product version information:";
oMainProductDetails = mProductDetails.foGetProductDetailsForMainModule();
aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
# Change order to put main product at the front:
aoProductDetails.remove(oMainProductDetails);
aoProductDetails.insert(0, oMainProductDetails);
for oProductDetails in aoProductDetails:
  print "+ \"%s\" version \"%s\" by \"%s\" installed in \"%s\"." % \
      (oProductDetails.sProductName, oProductDetails.oProductVersion, oProductDetails.sProductAuthor, oProductDetails.sInstallationFolderPath);
print;

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

aoLicenses = mProductDetails.faoGetLicensesFromRegistry();
print "Software license information in registry:";
if not aoLicenses:
  print "- No licenses loaded";
for oLicense in aoLicenses:
  print "+ %s is licensed to use %s for %s on %d systems until %s with authentication %s" % \
      (oLicense.sLicenseeName, fsToOxfordComma(oLicense.asProductNames), oLicense.sUsageTypeDescription, \
      oLicense.uLicensedInstances, oLicense.oEndDate, oLicense.sLicenseId);

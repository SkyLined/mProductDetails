import os, sys;

# Augment the search path: pretend we are in the parent folder so we can load mProductDetails as a module:
sTestsFolderPath = os.path.abspath(os.path.dirname(__file__));
sMainFolderPath = os.path.abspath(os.path.dirname(sTestsFolderPath));
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

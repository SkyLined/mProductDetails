import os;

gsDefaultLicenseFileName = "#license.asc";
goLicenseCollectionForAllLoadedProducts = None;
gbShowDebugOutput = False;

def foGetLicenseCollectionForAllLoadedProducts():
  global goLicenseCollectionForAllLoadedProducts;
  if goLicenseCollectionForAllLoadedProducts:
    return goLicenseCollectionForAllLoadedProducts;
  aoLoadedProductDetails = faoGetProductDetailsForAllLoadedModules();
  asLoadedProductNames = set([oProductDetails.sProductName for oProductDetails in aoLoadedProductDetails]);
  # Read all license stored in the registry:
  aoLicensesFromRegistry = cLicenseRegistryCache.faoReadLicensesFromRegistry();
#  print "Licenses cached in registry:";
#  if len(aoLicensesFromRegistry) == 0:
#    print "  - None";
#  for oLicense in aoLicensesFromRegistry:
#    print "  * %s for %s" % (oLicense.sLicenseId, "/".join(oLicense.asProductNames));

  doLicenseFromRegistry_by_sId = dict([(oLicense.sLicenseId, oLicense) for oLicense in aoLicensesFromRegistry]);
  # Select only licenses for any of the loaded products:
  aoLoadedProductLicenses = [
    oLicense for oLicense in aoLicensesFromRegistry
    if asLoadedProductNames & set(oLicense.asProductNames)
  ];
  # add all license stored in license files in the root folder of each loaded product:
  asErrors = [];
  asWarnings = [];
  for oProductDetails in aoLoadedProductDetails:
    sLicenseFilePath = os.path.join(oProductDetails.s0InstallationFolderPath, gsDefaultLicenseFileName);
    if not os.path.isfile(sLicenseFilePath):
      continue;
    try:
      aoLicensesFromFile = faoGetLicensesFromFile(sLicenseFilePath);
    except Exception as oException:
      asErrors.append("License file %s for product %s could not be read (%s)." % \
          (sLicenseFilePath, oProductDetails.sProductName, repr(oException)));
    else:
      if gbShowDebugOutput: print("Licenses read from %s:" % sLicenseFilePath);
      if not aoLicensesFromFile:
        asWarnings.append("No valid licenses were found in the file %s." % sLicenseFilePath);
      for oLicenseFromFile in aoLicensesFromFile:
        # Select only licenses for any of the loaded products:
        if not (asLoadedProductNames & set(oLicenseFromFile.asProductNames)):
          if gbShowDebugOutput: print("  - %s for %s (products not loaded)" % (oLicenseFromFile.sLicenseId, "/".join(oLicenseFromFile.asProductNames)));
          continue;
        # Add only licenses that were not already loaded from the registry:
        oLicenseFromRegistry = doLicenseFromRegistry_by_sId.get(oLicenseFromFile.sLicenseId);
        bWriteToRegistry = True;
        if oLicenseFromRegistry is None:
          if gbShowDebugOutput: print("  + %s for %s (new)" % (oLicenseFromFile.sLicenseId, "/".join(oLicenseFromFile.asProductNames)));
        elif sorted(oLicenseFromFile.asProductNames) != sorted(oLicenseFromRegistry.asProductNames):
          if gbShowDebugOutput: print("  + %s for %s (updated product names)" % (oLicenseFromFile.sLicenseId, "/".join(oLicenseFromFile.asProductNames)));
          # We may load the same license from file twice, but we can only remove it once:
          if oLicenseFromRegistry in aoLoadedProductLicenses:
            aoLoadedProductLicenses.remove(oLicenseFromRegistry);
          # We may be appending the same license twice here, but that should not have any negative effect on licensing.
          aoLoadedProductLicenses.append(oLicenseFromFile);
          asWarnings.append("The license with id %s has been updated using %s to apply to product %s using file %s." % \
              (oLicenseFromFile.sLicenseId, oLicenseFromFile.sLicenseSource, "/".join(oLicenseFromFile.asProductNames), sLicenseFilePath));
        else:
          if gbShowDebugOutput: print("  * %s for %s (already cached in registry)" % (oLicenseFromFile.sLicenseId, "/".join(oLicenseFromFile.asProductNames)));
          bWriteToRegistry = False;
        if bWriteToRegistry:
          oLicenseFromFile.fWriteToRegistry();
  # For products that have no active, valid license: add all licenses stored in files in the root folder of each product
  goLicenseCollectionForAllLoadedProducts = \
      cLicenseCollection(aoLoadedProductDetails, aoLoadedProductLicenses, asErrors, asWarnings);
  return goLicenseCollectionForAllLoadedProducts;

from .cLicense import cLicense;
from .cLicenseCollection import cLicenseCollection;
from .cLicenseRegistryCache import cLicenseRegistryCache;
from .faoGetLicensesFromFile import faoGetLicensesFromFile;
from .faoGetProductDetailsForAllLoadedModules import faoGetProductDetailsForAllLoadedModules;

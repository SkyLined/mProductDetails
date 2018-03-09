import os;
from .cLicense import cLicense;
from .cLicenseCollection import cLicenseCollection;
from .cLicenseRegistryCache import cLicenseRegistryCache;
from .faoGetProductDetailsForAllLoadedModules import faoGetProductDetailsForAllLoadedModules;

gsDefaultLicenseFileName = "#License.asc";

def foGetLicenseCollectionForAllLoadedProducts():
  aoLoadedProductDetails = faoGetProductDetailsForAllLoadedModules();
  asLoadedProductNames = [oProductDetails.sProductName for oProductDetails in aoLoadedProductDetails];
  # Read all license stored in the registry:
  aoLicensesFromRegistry = cLicenseRegistryCache.faoReadLicensesFromRegistry();
#  print "Licenses cached in registry:";
#  if len(aoLicensesFromRegistry) == 0:
#    print "  - None";
#  for oLicense in aoLicensesFromRegistry:
#    print "  * %s for %s" % (oLicense.sLicenseId, oLicense.sProductName);

  asLicenseIdsFromRegistry = [oLicense.sLicenseId for oLicense in aoLicensesFromRegistry];
  # Select only licenses for any of the loaded products:
  aoLoadedProductLicenses = [
    oLicense
    for oLicense in aoLicensesFromRegistry
    if oLicense.sProductName in asLoadedProductNames
  ];
  # add all license stored in license files in the root folder of each loaded product:
  asErrors = [];
  asWarnings = [];
  for oProductDetails in aoLoadedProductDetails:
    sLicenseFilePath = os.path.join(oProductDetails.sInstallationFolderPath, gsDefaultLicenseFileName);
    if not os.path.isfile(sLicenseFilePath):
      continue;
    try:
      oFile = open(sLicenseFilePath, "rb");
      try:
        sLicenseBlocks = oFile.read();
      finally:
        oFile.close();
    except:
      asErrors.append("License file %s could not be read." % (sLicenseFilePath, oProductDetails.sProductName));
#    print "Licenses read from %s:" % sLicenseFilePath;
    for oLicenseFromFile in cLicense.faoForLicenseBlocks(sLicenseBlocks):
      # Select only licenses for any of the loaded products:
      if oLicenseFromFile.sProductName not in asLoadedProductNames:
#        print "  - %s for %s (product not loaded)" % (oLicenseFromFile.sLicenseId, oLicenseFromFile.sProductName);
        continue;
      # Add only licenses that were not already loaded from the registry:
      if oLicenseFromFile.sLicenseId in asLicenseIdsFromRegistry:
#        print "  * %s for %s (already cached in registry)" % (oLicenseFromFile.sLicenseId, oLicenseFromFile.sProductName);
        continue;
#      print "  + %s for %s (new)" % (oLicenseFromFile.sLicenseId, oLicenseFromFile.sProductName);
      aoLoadedProductLicenses.append(oLicenseFromFile);
      if not oLicenseFromFile.fbWriteToRegistry():
        asWarnings.append("The license with id %s for product %s from file %s could not be cached in the registry." % \
            (oLicenseFromFile.sLincenseId, oLicenseFromFile.sProductName, sLicenseFilePath));
  # For products that have no active, valid license: add all licenses stored in files in the root folder of each product
  return cLicenseCollection(aoLoadedProductDetails, aoLoadedProductLicenses, asErrors, asWarnings);

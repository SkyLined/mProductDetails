import sys;
from .cProductDetails import cProductDetails;

def faoGetProductDetailsForAllLoadedModules():
  doProductDetails_by_sProductName = {};
  for mLoadedModule in sys.modules.values():
    oProductDetails = cProductDetails.foGetForModule(mLoadedModule);
    if oProductDetails:
      oExistingProductDetails = doProductDetails_by_sProductName.get(oProductDetails.sProductName);
      if oExistingProductDetails:
        assert oProductDetails.sInstallationFolderPath == oExistingProductDetails.sInstallationFolderPath, \
            "%s is loaded from both %s and %s!?" % \
            (oProductDetails.sInstallationFolderPath, oExistingProductDetails.sInstallationFolderPath);
      else:
        doProductDetails_by_sProductName[oProductDetails.sProductName] = oProductDetails;
  return doProductDetails_by_sProductName.values();


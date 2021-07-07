import sys;

def faoGetProductDetailsForAllLoadedModules():
  doProductDetails_by_sProductName = {};
  for mLoadedModule in sys.modules.values():
    o0ProductDetails = cProductDetails.fo0GetForModule(mLoadedModule);
    if o0ProductDetails is None: continue;
    oProductDetails = o0ProductDetails;
    oExistingProductDetails = doProductDetails_by_sProductName.get(oProductDetails.sProductName);
    if oExistingProductDetails:
      assert oProductDetails.s0InstallationFolderPath == oExistingProductDetails.s0InstallationFolderPath, \
          "%s is loaded from both %s and %s!?" % \
          (oProductDetails.s0InstallationFolderPath, oExistingProductDetails.s0InstallationFolderPath);
    else:
      doProductDetails_by_sProductName[oProductDetails.sProductName] = oProductDetails;
  return list(doProductDetails_by_sProductName.values());

from .cProductDetails import cProductDetails;

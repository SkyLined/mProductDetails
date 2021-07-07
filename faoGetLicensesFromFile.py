
def faoGetLicensesFromFile(sLicensesFilePath):
  try:
    from mFileSystemItem import cFileSystemItem;
  except:
    with open(sLicensesFilePath, "rb") as oLicensesFile:
      sbLicenseBlocks = oLicensesFile.read();
  else:
    sbLicenseBlocks = cFileSystemItem(sLicensesFilePath).fsbRead();
  return cLicense.faoForLicenseBlocks(sbLicenseBlocks, "license file %s" % sLicensesFilePath);
  
from .cLicense import cLicense;

def faoGetLicensesFromFile(sLicensesFilePath):
  try:
    from cFileSystemItem import cFileSystemItem;
  except:
    cFileSystemItem = None;
  if cFileSystemItem:
    sLicenseBlocks = cFileSystemItem(sLicenseFilePath).fsRead();
  else:
    with open(sLicensesFilePath) as oLicensesFile:
      sLicenseBlocks = oLicensesFile.read();
  
  return cLicense.faoForLicenseBlocks(sLicenseBlocks);
  
from .cLicense import cLicense;
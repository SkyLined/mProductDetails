
def fWriteLicensesToProductFolder(aoLicenses, oProductDetails):
  sbLicenseBlocks = b"\r\n".join([
    oLicense.sbLicenseBlock
    for oLicense in aoLicenses
  ]);
  try:
    from mFileSystemItem import cFileSystemItem;
  except:
    import os;
    sLicenseFilePath = os.path.join(oProductDetails.s0InstallationFolderPath, "#license.asc");
    with open(sLicensesFilePath, "wb") as oLicensesFile:
      oLicensesFile.write(sbLicenseBlocks);
  else:
    oLicenseFile = cFileSystemItem(oProductDetails.s0InstallationFolderPath).foGetChild("#license.asc");
    oLicenseFile.fbWrite(sbLicenseBlocks, bThrowErrors = True);


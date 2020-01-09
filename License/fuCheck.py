import os;

from mProductDetails.cProductDetails import cProductDetails;
from mProductDetails.cLicenseCheckServer import cLicenseCheckServer;
from mProductDetails.faoGetLicensesFromFile import faoGetLicensesFromFile;
from mProductDetails.faoGetLicensesFromRegistry import faoGetLicensesFromRegistry;

def fUsage(sMainScriptName, sFeatureName):
  ##############################################################################
  print "Check all licenses registered for use by the current user on this system or in";
  print "a license file.";
  print "Usage:";
  print "  %s %s [settings]" % (sMainScriptName, sFeatureName);
  print "  %s %s <license file path> [settings]" % (sMainScriptName, sFeatureName);
  print "Where <settings> are:";
  print "  --product=<product folder path>    The root folder for a product.";
  print "";
  print "This feature will check all licenses cached in the registry unless you specify";
  print "a license file it should read and check.";
  print "";
  print "The license server URL is taken from the product details stored in the current";
  print "folder or the folder you specify through the --product setting.";
  print "A valid product folder is required for this command to work.";

def fuCheck(sMainScriptName, sFeatureName, asArguments, dsArguments):
  # Parse arguments
  sProductFolderPath = None;
  for (sName, sValue) in dsArguments.items():
    if sName == "help":
      fUsage(sMainScriptName, sFeatureName);
      return 0;
    elif sName == "product":
      if sProductFolderPath is not None:
        print "- Please provide only one product folder path!";
        fUsage(sMainScriptName, sFeatureName);
        return 3;
      sProductFolderPath = sValue;
    else:
      print "- Unknown argument --%s!" % sName;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 2;
  if not sProductFolderPath:
    sProductFolderPath = os.getcwd();
  
  sLicenseFilePath = None;
  for sArgument in asArguments:
    if sLicenseFilePath is None:
      sLicenseFilePath = sArgument;
    else:
      print "- Superfluous argument %s!" % sArgument;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 2;
  
  oProductDetails = cProductDetails.foReadForFolderPath(sProductFolderPath);
  if not oProductDetails:
    print "Cannot find product details in folder %s." % sProductFolderPath;
    return 4;
  if not oProductDetails.sLicenseServerURL:
    print "The product (%s) does not have a license server." % oProductDetails.sProductName;
    return 6;
    
  print "Using license check server %s." % oProductDetails.sLicenseServerURL;
  oLicenseCheckServer = cLicenseCheckServer(oProductDetails.sLicenseServerURL);
  
  if sLicenseFilePath:
    aoLicenses = faoGetLicensesFromFile(sLicenseFilePath)
    if not aoLicenses:
      print "There are no licenses in the file";
      return 0;
  else:
    aoLicenses = faoGetLicensesFromRegistry();
    if not aoLicenses:
      print "There are no licenses in the registry";
      return 0;
  
  bInvalidLicenseFound = False;
  for oLicense in aoLicenses:
    print "License for %s with id %s:" % (oLicense.asProductNames[0], oLicense.sLicenseId);
    oLicenseCheckResult = oLicenseCheckServer.foGetLicenseCheckResult(oLicense, bCheckOnly = True);
    if not oLicenseCheckResult.bLicenseIsValid:
      print "- License is invalid.";
      bInvalidLicenseFound = True;
    else:
      print "+ License is valid.";
    if oLicenseCheckResult.bLicenseMayNeedToBeUpdated:
      print "  Note: You may need to download an updated version of this license.";
    if not oLicenseCheckResult.bInLicensePeriod:
      if oLicense.bIsExpired():
        print "- The license expired on %s." % oLicense.oEndDate.fsToHumanReadableString();
      else:
        print "- The license is not active until %s." % oLicense.oStartDate.fsToHumanReadableString();
    if oLicenseCheckResult.sLicenseIsRevokedForReason:
      print "- The license is revoked for the following reason:";
      print "  %s" % oLicense.sLicenseIsRevokedForReason;
    if oLicenseCheckResult.bDeactivatedOnSystem:
      print "- The license is deactivated on this system.";
    if oLicenseCheckResult.bLicenseInstancesExceeded:
      print "- You have exceeded the licensed instances.";
  return 7 if bInvalidLicenseFound else 1;


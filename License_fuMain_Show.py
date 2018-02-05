import re;

from mProductVersionAndLicense.cProductDetails import cProductDetails;
from mProductVersionAndLicense.cLicenseCheckRegistry import cLicenseCheckRegistry;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Show all licenses registered for use by the current user on this system.";
  print "Usage:";
  print "  %s %s <options>" % (sMainScriptName, sFeatureName);
  print "Where <options> is:";
  print " [[--product=]<product folder>]    The root folder for the product.";
  print "";
  print "This feature will show all licenses in the registry, or only those for a";
  print "specific product. When a specific product is provided, the licenses will";
  print "be checked for validity with the server";

def License_fuMain_Show(sMainScriptName, sFeatureName, asArguments):
  # Parse arguments
  sProductFolderPath = None;
  for sArgument in asArguments:
    oArgumentMatch = re.match(r"^\-\-([\w\-]+)(?:\=(.*))?$", sArgument);
    if not oArgumentMatch:
      if sProductFolderPath is None:
        sProductFolderPath = sArgument;
      else:
        print "- Superfluous argument %s!" % sArgument;
        return 1;
    else:
      (sName, sValue) = oArgumentMatch.groups();
      sName = sName.lower();
      if sName == "help":
        fUsage(sMainScriptName, sFeatureName);
        return 0;
      elif sName == "product":
        if sProductFolderPath is not None:
          print "- Please provide only one product folder path!";
          return 1;
        sProductFolderPath = sValue;
      else:
        print "- Unrecognized argument %s!" % sArgument;
        return 1;
  # Check arguments
  if sProductFolderPath is None:
    oProductDetails = None;
  else:
    # Read the product details from the product folder:
    oProductDetails = cProductDetails.foReadFromFolderPath(sProductFolderPath);
    if not oProductDetails:
      print "- Product details could not be read from %s!" % sProductFolderPath;
      return 2;
  
  oLicenseCollection = cLicenseCheckRegistry.foLicenseCollectionFromRegistry(
      sProductName = oProductDetails and oProductDetails.sProductName);
  # Read the licenses from the input file for the given product
  if len(oLicenseCollection.aoLicenses) == 0:
    print "- There are no licenses registered for the current user on this system!";
    return 2;
  # Check the licenses with the server:
  if oProductDetails:
    oLicenseCollection.fCheckWithServer(oProductDetails.oLicenseCheckServer, bWriteToRegistry = False); # Do not write to registry yet
  # See if there is a valid license for the product:
  uActiveNonInvalidLicensesCount = 0;
  for oLicense in oLicenseCollection.aoLicenses:
    print "  %s" % oLicense.sLicenseBlock.rstrip("\n").replace("\n", "\n  ");
    if oProductDetails and not oLicense.bIsValid:
      print "- This license is not valid!";
    elif oProductDetails and oLicense.bIsRevoked:
      print "- This license is revoked!";
    elif oProductDetails and oLicense.bLicenseInstancesExceeded:
      print "- This license has exceeded the allowed number of instances!";
    elif oLicense.bIsExpired:
      print "- This license has expired!";
    elif not oLicense.bIsActive:
      print "- This license is not yet active!";
    else:
      if oProductDetails:
        print "+ This license is valid and active.";
      else:
        print "+ This license is active.";
      uActiveNonInvalidLicensesCount += 1;
    print;
  if len(oLicenseCollection.aoLicenses) == 1:
    print "* Found one license, which is %svalid." % (uActiveNonInvalidLicensesCount == 0 and "not " or "");
  elif len(oLicenseCollection.aoLicenses) == uActiveNonInvalidLicensesCount:
    print "* Found %d licenses, which are all valid." % len(oLicenseCollection.aoLicenses);
  else:
    print "* Found %d licenses, %d of which %s valid." % (
      len(oLicenseCollection.aoLicenses),
      uActiveNonInvalidLicensesCount or "none",
      uActiveNonInvalidLicensesCount == 1 and "is" or "are",
    );
  if uActiveNonInvalidLicensesCount > 0:
    if oProductDetails:
      print;
      oFirstRunDate = cLicenseCheckRegistry.foGetFirstRunDate(oProductDetails.sProductName);
      if oFirstRunDate:
        print "+ %s was first run on %s." % (oProductDetails.sProductName, oFirstRunDate);
      else:
        print "+ You have not run %s yet." % oProductDetails.sProductName;
      print "Thank you for registering your product!";
    else:
      print;
      print "Please note that license validity can only be checked if you provide a";
      print "--product argument!";
    return 0;
  return 2;

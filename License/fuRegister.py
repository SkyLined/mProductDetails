import re;

from mProductDetails.cProductDetails import cProductDetails;
from mProductDetails.cLicenseCollection import cLicenseCollection;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Register a new licenses for a specific product for use by the current user on";
  print "this system.";
  print "Usage:";
  print "  %s %s <settings>" % (sMainScriptName, sFeatureName);
  print "Where <settings> are:";
  print " [--product=]<product folder>      The root folder for the product.";
  print " [--license=]<license file name>   Path to a file containing the license.";
  print "";
  print "This feature will check all the licenses in the input file that apply to the";
  print "product and ask the server if they are valid. Those that are valid are stored in";
  print "the registry for use with the product.";

def fuRegister(sMainScriptName, sFeatureName, asArguments, dsArguments):
  if len(asArguments) + len(dsArguments) == 0:
    fUsage(sMainScriptName, sFeatureName);
    return 1;
  
  # Parse arguments
  sProductFolderPath = None;
  sLicenseFilePath = None;
  for (sName, sValue) in dsArguments.items():
    sName = sName.lower();
    if sName == "help":
      fUsage(sMainScriptName, sFeatureName);
      return 0;
    elif sName == "product":
      if sProductFolderPath is not None:
        print "- Please provide only one product folder path!";
        fUsage(sMainScriptName, sFeatureName);
        return 1;
      sProductFolderPath = sValue;
    elif sName == "license":
      if sLicenseFilePath is not None:
        print "- Please provide only one input file path!";
        fUsage(sMainScriptName, sFeatureName);
        return 1;
      sLicenseFilePath = sValue;
    else:
      print "- Unknown argument --%s!" % sName;
      fUsage(sMainScriptName, sFeatureName);
      return 1;
  
  for sArgument in asArguments:
    if sProductFolderPath is None:
      sProductFolderPath = sArgument;
    elif sLicenseFilePath is None:
      sLicenseFilePath = sArgument;
    else:
      print "- Superfluous argument %s!" % sArgument;
      fUsage(sMainScriptName, sFeatureName);
      return 1;
  
  # Check arguments
  if sProductFolderPath is None:
    print "- Please provide a --product argument!";
    fUsage(sMainScriptName, sFeatureName);
    return 1;
  if sLicenseFilePath is None:
    print "- Please provide a --license argument!";
    fUsage(sMainScriptName, sFeatureName);
    return 1;

  # Read the product details from the product folder:
  oProductDetails = cProductDetails.foReadForFolderPath(sProductFolderPath);
  if not oProductDetails:
    print "- Product details could not be read from %s!" % sProductFolderPath;
    return 2;
  # Read the licenses from the input file for the given product
  oLicenseCollection = cLicenseCollection.foReadFromFile(sLicenseFilePath, sProductName = oProductDetails.sProductName);
  if not oLicenseCollection:
    print "- Licenses could not be read from %s!" % sLicenseFilePath;
  # Check the licenses with the server:
  oLicenseCollection.fCheckWithServer(oProductDetails.oLicenseCheckServer, bWriteToRegistry = False); # Do not write to registry yet
  # See if there is a valid license for the product:
  aoValidLicenses = [];
  bFoundErrors = False;
  for oLicense in oLicenseCollection.aoLicenses:
    if not oLicense.bIsValid:
      print "- License %s is not valid!" % oLicense.sLicenseId;
    elif oLicense.bIsRevoked:
      print "- License %s is revoked!" % oLicense.sLicenseId;
    elif oLicense.bLicenseInstancesExceeded:
      print "- License %s has exceeded the allowed number of instances!" % oLicense.sLicenseId;
    elif not oLicense.fbWriteToRegistry():
      print "- License %s cannot be written to the registry!" % oLicense.sLicenseId;
    else:
      aoValidLicenses.append(oLicense);
      continue; # Do not set bFoundErrors;
    bFoundErrors = True;
  if bFoundErrors:
    print;
  if not aoValidLicenses:
    print "We're sorry: no valid licenses were found!";
    return 2;
  print "Congratulations! %s%d valid license%s found and registered:" % (
    bFoundErrors and "Dispite the above errors, " or "",
    len(aoValidLicenses),
    len(aoValidLicenses) == 1 and " was" or "s were",
  );
  for oLicense in aoValidLicenses:
    print oLicense.sLicenseBlock;
  print;
  print "Thank you for registering your product!";
  return 0;

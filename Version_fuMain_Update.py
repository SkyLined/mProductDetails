import re;

from mProductVersionAndLicense.cProductDetails import cProductDetails;
from mProductVersionAndLicense.cVersion import cVersion;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Update a products version in the dxProductDetails.json file.";
  print "Usage:";
  print "  %s %s <options>" % (sMainScriptName, sFeatureName);
  print "Where <options> is:";
  print " [--product=]<product folder>    The root folder for the product.";

def Version_fuMain_Update(sMainScriptName, sFeatureName, asArguments):
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
    print "- Please provide a --product argument!";
    return 1;
  # Read the product details from the product folder:
  oProductDetails = cProductDetails.foReadFromFolderPath(sProductFolderPath);
  if not oProductDetails:
    print "- Product details could not be read from %s!" % sProductFolderPath;
    return 2;
  oProductDetails.oProductVersion = cVersion.foNew();
  if not oProductDetails.fbWriteToFolderPath(sProductFolderPath):
    print "- Product details could not be written to %s!" % sProductFolderPath;
    return 2;
  print "+ Version updated to %s." % oProductDetails.oProductVersion;
  return 0;

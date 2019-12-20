from mProductDetails.cProductDetails import cProductDetails;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Show the version stored in the dxProductDetails.json file of a product.";
  print "Usage:";
  print "  %s %s <settings>" % (sMainScriptName, sFeatureName);
  print "Where <settings> are:";
  print " [--product=]<product folder>    The root folder for the product.";

def fuShow(sMainScriptName, sFeatureName, asArguments, dsArguments):
  if len(asArguments) + len(dsArguments) == 0:
    fUsage(sMainScriptName, sFeatureName);
    return 1;
  
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
      fUsage(sMainScriptName, sFeatureName);
      return 3;
  
  for sArgument in asArguments:
    if sProductFolderPath is None:
      sProductFolderPath = sArgument;
    else:
      print "- Superfluous argument %s!" % asArguments[0];
      fUsage(sMainScriptName, sFeatureName);
      return 3;
  
  # Check arguments
  if sProductFolderPath is None:
    print "- Please provide a --product argument!";
    fUsage(sMainScriptName, sFeatureName);
    return 3;
  
  # Read the product details from the product folder:
  oProductDetails = cProductDetails.foReadForFolderPath(sProductFolderPath);
  if not oProductDetails:
    print "- Product details could not be read from %s!" % sProductFolderPath;
    return 4;
  print "+ Version %s." % oProductDetails.oProductVersion;
  return 0;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Show all licenses registered for use by the current user on this system or in";
  print "a license file.";
  print "Usage:";
  print "  %s %s" % (sMainScriptName, sFeatureName);
  print "  %s %s <license file path>" % (sMainScriptName, sFeatureName);
  print "";
  print "This feature will show all licenses cached in the registry unless you specify";
  print "a license file it should read them from.";

def fuShow(sMainScriptName, sFeatureName, asArguments, dsArguments):
  # Parse arguments
  for (sName, sValue) in dsArguments.items():
    if sName == "help":
      fUsage(sMainScriptName, sFeatureName);
      return 2;
    else:
      print "- Unknown argument --%s!" % sName;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 2;
  
  sLicenseFilePath = None;
  for sArgument in asArguments:
    if sLicenseFilePath is None:
      sLicenseFilePath = sArgument;
    else:
      print "- Superfluous argument %s!" % sArgument;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 2;
  
  if sLicenseFilePath:
    from mProductDetails.faoGetLicensesFromFile import faoGetLicensesFromFile;
    aoLicenses = faoGetLicensesFromFile(sLicenseFilePath)
    if not aoLicenses:
      print "There are no licenses in the file";
      return 0;
  else:
    from mProductDetails.faoGetLicensesFromRegistry import faoGetLicensesFromRegistry;
    aoLicenses = faoGetLicensesFromRegistry();
    if not aoLicenses:
      print "There are no licenses in the registry";
      return 0;
  
  for oLicense in aoLicenses:
    print oLicense.sLicenseBlock;
  return 1;


import re;

from mProductDetails.faoGetLicensesFromRegistry import faoGetLicensesFromRegistry;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Show all licenses registered for use by the current user on this system.";
  print "Usage:";
  print "  %s %s" % (sMainScriptName, sFeatureName);
  print "";
  print "This feature will show all licenses cached in the registry.";

def fuShow(sMainScriptName, sFeatureName, asArguments, dsArguments):
  # Parse arguments
  sProductFolderPath = None;
  sLicenseFilePath = None;
  for (sName, sValue) in dsArguments.items():
    if sName == "help":
      fUsage(sMainScriptName, sFeatureName);
      return 0;
    else:
      print "- Unknown argument --%s!" % sName;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 1;
  
  for sArgument in asArguments:
      print "- Superfluous argument %s!" % sArgument;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 1;
  
  aoLicenses = faoGetLicensesFromRegistry();
  if not aoLicenses:
    print "There are no licenses in the registry";
  for oLicense in aoLicenses:
    print oLicense.sLicenseBlock;
  return 0;


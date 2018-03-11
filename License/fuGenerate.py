import re, os;

from mProductDetails.cDate import cDate;
from mProductDetails.cProductDetails import cProductDetails;
from mProductDetails.cLicenseConfiguration import cLicenseConfiguration;
from mProductDetails.cLicenseCheckServer import cLicenseCheckServer;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Generate new licenses for a specific product";
  print "Usage:";
  print "  %s %s <settings> <options>" % (sMainScriptName, sFeatureName);
  print "Where <settings> are:";
  print " [--product=]<product folder>      The root folder for the product.";
  print " [--config=]<config file name>     Path to a license configuration file.";
  print " [--licensee=]<licensee name>      Name of the licensee.";
  print " [--use=]<usage keyword>           Licensed usage keyword; valid values depend";
  print "                                   on the selected license configuration."
  print "And <options> are:";
  print " [--version=<version>]             Select a license version (optional).";
  print " [--instances=<number>]            Maximum number of instances for the license";
  print "                                   (optional; default = 1).";
  print " [--start=<YYYY-MM-DD date>]       Start date (optional; default = today).";
  print " [--end=<YYYY-MM-DD date>]         End date (optional).";
  print " [--duration=<#y+#m+#d duration>]  Duration (optional; default = 1y+7d when";
  print "                                   starting today, otherwise 1y)";
  print " [--output=<license file name>]    Where to write the generated license.";
  print "";
  print "This feature will generate a new license for given settings, check with the";
  print "server that the license is considered valid and write it to a file.";
  print "Note that you can provide multiple product folders to generate licenses for";
  print "multiple products with the same settings by using the --products setting:";
  print "  --products=<product folder>|<product folder>|...";


def fuGenerate(sMainScriptName, sFeatureName, asArguments, dsArguments):
  # Parse arguments
  asProductFolderPaths = [];
  sLicenseConfigurationFilePath = None;
  sLicenseVersion = None;
  sLicenseeName = None;
  sUsageTypeKeyword = None;
  uLicensedInstances = 1;
  bGenerateServerCheckPostData = False;
  oStartDate = cDate.foNow();
  oEndDate = None;
  sDuration = None;
  sOutputFilePath = None;
  for (sName, sValue) in dsArguments.items():
    if sName == "help":
      fUsage(sMainScriptName, sFeatureName);
      return 0;
    elif sName == "product":
      asProductFolderPaths = [sValue];
    elif sName == "products":
      asProductFolderPaths = sValue.split("|");
    elif sName == "config":
      sLicenseConfigurationFilePath = sValue;
    elif sName == "version":
      sLicenseVersion = sValue;
    elif sName == "licensee":
      sLicenseeName = sValue;
    elif sName == "use":
      sUsageTypeKeyword = sValue;
    elif sName == "instances":
      uLicensedInstances = long(sValue);
    elif sName == "start":
      oStartDate = cDate.foFromString(sValue);
    elif sName == "end":
      oEndDate = cDate.foFromString(sValue);
    elif sName == "duration":
      sDuration = sValue;
    elif sName == "output":
      sOutputFilePath = sValue;
    else:
      print "- Unknown argument --%s!" % sName;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 1;
  
  for sArgument in asArguments:
    if len(asProductFolderPaths) == 0:
      asProductFolderPaths.append(sArgument);
    elif sLicenseConfigurationFilePath is None:
      sLicenseConfigurationFilePath = sArgument;
    elif sLicenseeName is None:
      sLicenseeName = sArgument;
    elif sUsageTypeKeyword is None:
      sUsageTypeKeyword = sArgument;
    else:
      print "- Superfluous argument %s!" % sArgument;
      print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
      return 1;
  
  # Check arguments
  if len(asProductFolderPaths) == 0:
    print "- Please provide at least one --product argument!";
    print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
    return 1;
  if sLicenseConfigurationFilePath is None:
    print "- Please provide a --config argument!";
    print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
    return 1;
  if sLicenseeName is None:
    print "- Please provide a --licensee argument!";
    print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
    return 1;
  if sUsageTypeKeyword is None:
    print "- Please provide a --use argument!";
    print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
    return 1;
  if oEndDate is not None and sDuration is not None:
    print "- Please provide either an --end or a --duration argument, not both!";
    print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
    return 1;
  if sDuration is not None:
    for sDurationComponent in sDuration.split("+"):
      oDurationMatch = re.match(r"(\d+)([ymd])", sDurationComponent, re.I);
      if oDurationMatch is None:
        print "- Please provide a valid value for the --duration argument!";
        print "  Run \"%s %s --help\" for help." % (sMainScriptName, sFeatureName);
        return 1;
  # Read the license configuration from the file:
  aoOrderedLicenseConfigurations = cLicenseConfiguration.faoReadFromJSONFile(sLicenseConfigurationFilePath);
  if not  aoOrderedLicenseConfigurations:
    print "- License configurations could not be read from %s" % sLicenseConfigurationFilePath;
    return 2;
#  print "+ Read %d license configurations from %s." % (len(aoOrderedLicenseConfigurations), sLicenseConfigurationFilePath);
  
  if sOutputFilePath:
    sLicenseBlocks = "";
  for sProductFolderPath in asProductFolderPaths:
    # Read the product details from the product folder:
    oProductDetails = cProductDetails.foReadForFolderPath(sProductFolderPath);
    if not oProductDetails:
      print "- Product details could not be read from %s!" % sProductFolderPath;
      return 2;

    # Filter license configurations for product name
    aoSelectedOrderedLicenseConfigurations = [
      oLicenseConfiguration for oLicenseConfiguration in aoOrderedLicenseConfigurations
      if oProductDetails.sProductName == oLicenseConfiguration.sProductName
    ];
    if not aoSelectedOrderedLicenseConfigurations:
      print "- No license configurations are available for product %s" % oProductDetails.sProductName;
      return 1;
#    if len(aoOrderedLicenseConfigurations) != len(aoSelectedOrderedLicenseConfigurations):
#      print "+ Selected %d license configurations for product %s." % \
#          (len(aoSelectedOrderedLicenseConfigurations), oProductDetails.sProductName);
    if sLicenseVersion:
      # Filter for version
      aoSelectedOrderedLicenseConfigurations = [
        oLicenseConfiguration for oLicenseConfiguration in aoSelectedOrderedLicenseConfigurations
        if oLicenseConfiguration.sVersion == sLicenseVersion
      ];
      if len(aoSelectedOrderedLicenseConfigurations) == 0:
        print "- No license configurations are available for product %s and version %s" % \
            (oProductDetails.sProductName, sLicenseVersion);
        return 1;
      assert len(aoSelectedOrderedLicenseConfigurations) == 1, \
          "There are multiple license configurations available for products %s and version %s" % \
            (oProductDetails.sProductName, sLicenseVersion);
    # Select the latest
    oLicenseConfiguration = aoSelectedOrderedLicenseConfigurations[-1];
#    if len(aoSelectedOrderedLicenseConfigurations) > 1:
#      print "+ Selected license configurations version %s." % (oLicenseConfiguration.sLicenseVersion);
    # Apply start/end dates
    if oEndDate is not None:
      pass;
    elif oStartDate == cDate.foNow():
      oEndDate = oStartDate.foEndDateForDuration(sDuration or "1y+7d");
    else:
      oEndDate = oStartDate.foEndDateForDuration(sDuration or "1y");
    # Create a new license.
    oLicense = oLicenseConfiguration.foCreateLicense(
      oProductDetails.sProductName, sLicenseeName, sUsageTypeKeyword, uLicensedInstances, oStartDate, oEndDate,
    );
    print oLicense.sLicenseBlock;
    # Check to make sure the server considers the license valid, but do not cache the result in the registry as this
    # may not be our own certificate:
    oLicenseCheckServer = cLicenseCheckServer(oProductDetails.sLicenseServerURL);
    try:
      oLicenseCheckResult = oLicenseCheckServer.foGetRegisterLicenseCheckResult(oLicense);
    except cLicenseCheckServer.cServerErrorException, oServerErrorException:
      print "- The server reported an error: %s" % oServerErrorException.sMessage;
      return 2;
    if not oLicenseCheckResult.bLicenseIsValid:
      print "- The server reported the new generated license as invalid!";
      return 2;
    # The below errors should be impossible, but it doesn't hurt to be thorough.
    if oLicenseCheckResult.sLicenseIsRevokedForReason:
      print "- The server reported the new generated license as revoked!";
      print "  Reason: %s" % sLicenseIsRevokedForReason;
      return 2;
    if oLicenseCheckResult.bLicenseInstancesExceeded:
      print "- The server reported the new generated license as having exceeded the licensed number of instances!";
      return 2;
    if sOutputFilePath:
      sLicenseBlocks += oLicense.sLicenseBlock;
  
  if sOutputFilePath:
    oOutputFile = open(sOutputFilePath, "wb");
    try:
      oOutputFile.write(sLicenseBlocks);
    finally:
      oOutputFile.close();
    print "+ The license%s been written to %s." % (len(asProductFolderPaths) == 1 and " has" or "s have", sOutputFilePath);
  
  return 0;
import json, os, re, sys, datetime;

sMainFolderPath = os.path.dirname(os.path.abspath(__file__));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
asOriginalSysPath = sys.path[:];
sys.path = [sMainFolderPath, sParentFolderPath, sModulesFolderPath] + sys.path;

from mProductVersionAndLicense.cDate import cDate;
from mProductVersionAndLicense.cProductDetails import cProductDetails;
from mProductVersionAndLicense.cLicenseConfiguration import cLicenseConfiguration;

# Restore the search path
sys.path = asOriginalSysPath;

def fUsage(sMainScriptName, sFeatureName):
         ################################################################################
  print "Generate new licenses for a specific product";
  print "Usage:";
  print "  %s %s <options>" % (sMainScriptName, sFeatureName);
  print "Where <options> is:";
  print " [--product=]<product folder>      The root folder for the product.";
  print " [--config=]<config file name>     Path to a license configuration file.";
  print " [--version=<version>]             Select a license version (optional).";
  print "  --licensee=<licensee name>       Name of the licensee.";
  print "  --use=<usage keyword>            Licensed usage keyword; valid values depend";
  print "                                   on the selected license configuration."
  print " [--instances=<maximum>]           Maximum number of instances for the license";
  print "                                   (optional; default = 1).";
  print " [--start-date=<Y-M-D date>]       Start date (optional; default = today).";
  print " [--end-date=<Y-M-D> date]         End date (optional).";
  print " [--duration=<Ny/m/d duration>]    Duration (optional; default = 1y).";
  print " [--output=<license file name>]    Where to write the generated license.";
  print "";
  print "This feature will generate a new license for given settings, check with the";
  print "server that the license is considered valid and write it to a file.";

def License_fuMain_Generate(sMainScriptName, sFeatureName, asArguments):
  if len(asArguments) == 0:
    fUsage(sMainScriptName, sFeatureName);
    return 1;
  sProductFolderPath = None;
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
  for sArgument in asArguments:
    oArgumentMatch = re.match(r"^\-\-([\w\-]+)(?:\=(.*))?$", sArgument);
    if not oArgumentMatch:
      if sProductFolderPath is None:
        sProductFolderPath = sArgument;
      elif sLicenseConfigurationFilePath is None:
        sLicenseConfigurationFilePath = sArgument;
      else:
        print "- Superfluous argument %s!" % sArgument;
        return 1;
    else:
      (sName, sValue) = oArgumentMatch.groups();
      if sName == "help":
        fUsage(sMainScriptName, sFeatureName);
        return 0;
      elif sName == "product":
        sProductFolderPath = sValue;
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
        print "- Unrecognized argument %s!" % sArgument;
        return 1;
  # Check arguments
  if sProductFolderPath is None:
    print "- Please provide a --product argument!";
    return 1;
  if sLicenseConfigurationFilePath is None:
    print "- Please provide an --config argument!";
    return 1;
  if sLicenseeName is None:
    print "- Please provide an --licensee argument!";
    return 1;
  if sUsageTypeKeyword is None:
    print "- Please provide an --use argument!";
    return 1;
  if oEndDate is not None and sDuration is not None:
    print "- Please provide either --end or --duration, not both!";
    return 1;
  oDurationMatch = None;
  if sDuration is not None:
    oDurationMatch = re.match(r"(\d+)([ymd])", sDuration.lower());
    if oDurationMatch is None:
      print "- Please provide a valid value (<number>[ymd]) for duration!";
      return 1;
  
  # Read the product details from the product folder:
  oProductDetails = cProductDetails.foReadFromFolderPath(sProductFolderPath);
  if not oProductDetails:
    print "- Product details could not be read from %s!" % sProductFolderPath;
    return 2;
  # Read the license configuration from the file:
  aoOrderedLicenseConfigurations = cLicenseConfiguration.faoReadFromJSONFile(sLicenseConfigurationFilePath);
  if not  aoOrderedLicenseConfigurations:
    print "- License configurations could not be read from %s" % sLicenseConfigurationFilePath;
    return 2;
  print "+ Read %d license configurations from %s." % (len(aoOrderedLicenseConfigurations), sLicenseConfigurationFilePath);

  # Filter license configurations for product name
  aoOrderedLicenseConfigurations = [
    oLicenseConfiguration for oLicenseConfiguration in aoOrderedLicenseConfigurations
    if oProductDetails.sProductName in oLicenseConfiguration.asProductNames
  ];
  if not aoOrderedLicenseConfigurations:
    print "- No license configurations are available for product %s" % oProductDetails.sProductName;
    return 1;
  print "+ Selected %d license configurations for product %s." % \
      (len(aoOrderedLicenseConfigurations), oProductDetails.sProductName);
  if sLicenseVersion:
    # Filter for version
    aoOrderedLicenseConfigurations = [
      oLicenseConfiguration for oLicenseConfiguration in aoOrderedLicenseConfigurations
      if oLicenseConfiguration.sVersion == sLicenseVersion
    ];
    if len(aoOrderedLicenseConfigurations) == 0:
      print "- No license configurations are available for product %s and version %s" % \
          (oProductDetails.sProductName, sLicenseVersion);
      return 1;
    assert len(aoOrderedLicenseConfigurations) == 1, \
        "There are multiple license configurations available for products %s and version %s" % \
          (oProductDetails.sProductName, sLicenseVersion);
  # Select the latest
  oLicenseConfiguration = aoOrderedLicenseConfigurations[-1];
  print "+ Selected license configurations version %s." % (oLicenseConfiguration.sLicenseVersion);
  # Apply start/end dates
  if oEndDate is not None:
    pass;
  else:
    oEndDate = oStartDate.foEndDateForDuration(sDuration or "1y");
  # Create a new license.
  oLicense = oLicenseConfiguration.foCreateLicense(
    oProductDetails.sProductName, sLicenseeName, sUsageTypeKeyword, uLicensedInstances, oStartDate, oEndDate,
  );
  print oLicense.sLicenseBlock;
  # Check to make sure the server considers the license valid, but do not cache the result in the registry as this
  # may not be our own certificate:
  oLicense.fCheckWithServer(oProductDetails.oLicenseCheckServer, bWriteToRegistry = False);
  if not oLicense.bIsValid:
    print "- The server reported the new generated license as invalid!";
    return 2;
  if oLicense.bIsRevoked:
    print "- The server reported the new generated license as revoked!";
    return 2;
  if oLicense.bLicenseInstancesExceeded:
    print "- The server reported the new generated license as having exceeded the licensed number of instances!";
    return 2;
  if sOutputFilePath:
    open(sOutputFilePath, "wb").write(oLicense.sLicenseBlock);
    print "+ The new license has been written to file.";
  return 0;
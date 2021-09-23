from fTestDependencies import fTestDependencies;
fTestDependencies();

try: # mDebugOutput use is Optional
  import mDebugOutput as m0DebugOutput;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mDebugOutput'":
    raise;
  m0DebugOutput = None;

guExitCodeInternalError = 1; # Use standard value;
try:
  try:
    from mConsole import oConsole;
  except:
    import sys, threading;
    oConsoleLock = threading.Lock();
    class oConsole(object):
      @staticmethod
      def fOutput(*txArguments, **dxArguments):
        sOutput = "";
        for x in txArguments:
          if isinstance(x, str):
            sOutput += x;
        sPadding = dxArguments.get("sPadding");
        if sPadding:
          sOutput.ljust(120, sPadding);
        oConsoleLock.acquire();
        print(sOutput);
        sys.stdout.flush();
        oConsoleLock.release();
      @staticmethod
      def fStatus(*txArguments, **dxArguments):
        pass;
  
  import os, sys;
  
  import mProductDetails;
  
  print("Unique system id: " + mProductDetails.fsGetSystemId());
  
  print("Product version information:");
  o0MainProductDetails = mProductDetails.fo0GetProductDetailsForModule(mProductDetails);
  assert o0MainProductDetails is not None, \
      "Cannot get product details for mProductDetails!?";
  oMainProductDetails = o0MainProductDetails;
  aoProductDetails = mProductDetails.faoGetProductDetailsForAllLoadedModules();
  # Change order to put main product at the front:
  aoProductDetails.remove(oMainProductDetails);
  aoProductDetails.insert(0, oMainProductDetails);
  for oProductDetails in aoProductDetails:
    print("+ \"%s\" version \"%s\" by \"%s\" installed in \"%s\"." % \
        (oProductDetails.sProductName, oProductDetails.oProductVersion, oProductDetails.sProductAuthor, oProductDetails.s0InstallationFolderPath));
  print();
  
  print("Checking licenses for loaded software products:");
  oLicenseCollection = mProductDetails.foGetLicenseCollectionForAllLoadedProducts();
  (asErrors, asWarnings) = oLicenseCollection.ftasGetLicenseErrorsAndWarnings();
  if asErrors:
    print("Software license error%s:" % (len(asErrors) > 1 and "s" or ""));
    for sError in asErrors:
      print("- " + sError);
    print();
  
  if asWarnings:
    print("Software license warning%s:" % (len(asWarnings) > 1 and "s" or ""));
    for sWarning in asWarnings:
      print("* " + sWarning);
    print();
  
  print("Software license information in registry:");
  aoLicenses = mProductDetails.faoGetLicensesFromRegistry();
  if not aoLicenses:
    print("- No licenses loaded");
  for oLicense in aoLicenses:
    print("+ %s licensed to %s:" % (oLicense.asProductNames[0], oLicense.sLicenseeName));
    print("  Products   : %s" % " | ".join(oLicense.asProductNames));
    print("  Usage type : %s" % oLicense.sUsageTypeDescription);
    print("  Instances  : %s" % oLicense.uLicensedInstances);
    print("  End date   : %s" % oLicense.oEndDate.fsToHumanReadableString());
    print("  Id         : %s" % oLicense.sLicenseId);
  
except Exception as oException:
  if m0DebugOutput:
    m0DebugOutput.fTerminateWithException(oException, guExitCodeInternalError, bShowStacksForAllThread = True);
  raise;

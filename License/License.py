import os, re, sys;

# This script should be run as if mProductDetails is a module, so we need to
# alter the search path:
sMainFolderPath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
asOriginalSysPath = sys.path[:];
sys.path = [sMainFolderPath, sParentFolderPath, sModulesFolderPath] + sys.path;

from fuGenerate import fuGenerate;
from fuRegister import fuRegister;
from fuShow import fuShow;

# Restore the search path
sys.path = asOriginalSysPath;

dFeature_fuMain_by_sName = {
  "generate": fuGenerate,
  "register": fuRegister,
  "show": fuShow,
};
dFeature_sDescription_by_sName = {
  "generate": "generate a new license.",
  "register": "register a license on this system.",
  "show":     "show licenses registered on this system.",
};

def fUsage(sMainScriptName):
  print "Usage:";
  print "  %s <feature> [feature arguments]" % sMainScriptName;
  print "";
  print "Where <feature> is anyone of the following:";
  for (sName, sFeatureDescription) in dFeature_sDescription_by_sName.items():
    print "  %-10s %s" % (sName, sFeatureDescription);
  print "";
  print "For more details about a specific feature, use --help, as in:";
  print "  %s <feature> --help" % sMainScriptName;


def fuMain(sMainScriptName, asArguments):
  if len(asArguments) == 0:
    fUsage(sMainScriptName);
    return 0;
  sFeatureName = asArguments[0].lower();
  asFeatureArguments = [];
  dsFeatureArguments = {};
  for sArgument in asArguments[1:]:
    oArgumentMatch = re.match(r"^\-\-([\w\-]+)(?:\=(.*))?$", sArgument);
    if oArgumentMatch:
      (sName, sValue) = oArgumentMatch.groups();
      dsFeatureArguments[sName.lower()] = sValue;
    else:
      asFeatureArguments.append(sArgument);
  
  fuFeatureMain = dFeature_fuMain_by_sName.get(sFeatureName);
  if fuFeatureMain is None:
    print "Unknown feature %s" % sFeatureName;
    return 1;
  return fuFeatureMain(sMainScriptName, sFeatureName, asFeatureArguments, dsFeatureArguments);

if __name__ == "__main__":
  os._exit(fuMain(sys.argv[0], sys.argv[1:]));

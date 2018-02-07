import json, os, re, sys, time;

sMainFolderPath = os.path.dirname(os.path.abspath(__file__));
sParentFolderPath = os.path.normpath(os.path.join(sMainFolderPath, ".."));
sModulesFolderPath = os.path.join(sMainFolderPath, "modules");
asOriginalSysPath = sys.path[:];
sys.path = [sMainFolderPath, sParentFolderPath, sModulesFolderPath] + sys.path;

from mProductVersionAndLicense.Version_fuMain_Update import Version_fuMain_Update;

# Restore the search path
sys.path = asOriginalSysPath;

dFeature_fuMain_by_sName = {
  "update": Version_fuMain_Update,
};
dFeature_sDescription_by_sName = {
  "update": "update a products version number.",
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
  asFeatureArguments = asArguments[1:];
  fuFeatureMain = dFeature_fuMain_by_sName.get(sFeatureName);
  if fuFeatureMain is None:
    print "Unknown feature %s" % sFeatureName;
    return 1;
  return fuFeatureMain(sMainScriptName, sFeatureName, asFeatureArguments);

if __name__ == "__main__":
  os._exit(fuMain(sys.argv[0], sys.argv[1:]));

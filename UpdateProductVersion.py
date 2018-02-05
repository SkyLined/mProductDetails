import json, re, time;

if __name__ == "__main__":
  sProductDetailsJSONFilePath = sys.argv[1];
  dsProjectDetails = json.loads(open(sProductDetailsJSONFilePath, "rb").read());
  sOldVersion = dsProjectDetails["sProductVersion"];
  sNewVersion = time.strftime("%Y-%m-%d %H:%M");
  if sOldVersion == sNewVersion:
    print "Version was updated less than one minute ago, cannot updating at this time.";
  else:
    dsProjectDetails["sProductVersion"] = sNewVersion;
    open(sProductDetailsJSONFilePath, "wb").write(re.sub(r"\r?\n", "\r\n", json.dumps(dsProjectDetails, sort_keys = True, indent = 2)));
    print "Version updated from %s to %s" % (sOldVersion, sNewVersion);

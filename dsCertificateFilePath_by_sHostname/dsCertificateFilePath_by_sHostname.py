import os;
sLocalPath = os.path.dirname(__file__);

dsCertificateFilePath_by_sHostname = {
  "license.skylined.nl": os.path.join(sLocalPath, "license.skylined.nl.crt"),
  "github.com": os.path.join(sLocalPath, "github.com.crt"),
};
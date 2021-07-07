import ssl, urllib.request, urllib.parse, urllib.error;

try:
  from mNotProvided import fAssertType as f0AssertType, fAssertTypes as f0AssertTypes;
except ModuleNotFoundError as oException:
  if oException.args[0] != "No module named 'mNotProvided'":
    raise;
  f0AssertType = f0AssertTypes = None;

# The rest of the imports are at the end to prevent import loops.

def fsbGetHTTPResponseData(sbURL, sb0PostData = None, sURLNameInException = None):
  if f0AssertTypes: f0AssertTypes({
    "sbURL": (sbURL, bytes),
    "sb0PostData": (sb0PostData, bytes, None),
    "sURLNameInException": (sURLNameInException, str),
  });
  sURL = str(sbURL, "ascii", "strict");
  try:
    oURL = urllib.parse.urlparse(sURL);
  except urllib.error.URLError as oException:
    raise AssertionError(
      "%s does not have a valid URL (URL: %s, error: %s)" % (sURLNameInException, repr(sbURL), repr(oException))
    );
  if oURL.scheme == "https":
    sCertificateFilePath = dsCertificateFilePath_by_sHostname.get(oURL.hostname);
    if sCertificateFilePath:
      # For use with site-pinning.
      oSSLContext = ssl.create_default_context(cafile = sCertificateFilePath);
    else:
      oSSLContext = ssl.create_default_context();
      oSSLContext.load_default_certs();
  else:
    oSSLContext = None;
  try:
    oHTTPRequest = urllib.request.urlopen(sURL, sb0PostData, context = oSSLContext);
  except urllib.error.HTTPError as oHTTPException:
    raise cServerResponseException(
      "%s could not be contacted (error: %s)" % (sURLNameInException, repr(oHTTPException)),
      {"sbURL": sbURL, "o0HTTPException": oHTTPException, "u0StatusCode": None, "sb0Data": None},
    );
  uStatusCode = oHTTPRequest.getcode();
  sbData = oHTTPRequest.read();
  if uStatusCode == 404:
    raise cServerResponseException(
      "%s was not found (HTTP 404)." % sURLNameInException,
      {"sbURL": sbURL, "o0HTTPException": None, "u0StatusCode": uStatusCode, "sb0Data": sbData},
    );
  if uStatusCode >= 500:
    raise cServerResponseException(
      "%s returned an internal error code %03d." % (sURLNameInException, uStatusCode),
      {"sbURL": sbURL, "o0HTTPException": None, "u0StatusCode": uStatusCode, "sb0Data": sbData},
    );
  if uStatusCode != 200:
    raise cServerResponseException(
      "%s returned an unexpected response code %03d." % (sURLNameInException, uStatusCode),
      {"sbURL": sbURL, "o0HTTPException": None, "u0StatusCode": uStatusCode, "sb0Data": sbData},
    );
  if not sbData:
    raise cServerResponseException(
      "%s did not return any data." % sURLNameInException,
      {"sbURL": sbURL, "o0HTTPException": None, "u0StatusCode": uStatusCode, "sb0Data": sbData},
    );
  return sbData;

from .dsCertificateFilePath_by_sHostname import dsCertificateFilePath_by_sHostname;
from .mExceptions import *;

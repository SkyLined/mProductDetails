import ssl, urllib, urlparse;
from .dsCertificateFilePath_by_sHostname import dsCertificateFilePath_by_sHostname;

def fsGetHTTPResponseData(sURL, sPostData, sURLNameInException, cException):
  oURL = urlparse.urlparse(sURL);
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
    oHTTPRequest = urllib.urlopen(sURL, sPostData, context = oSSLContext);
  except Exception as oException:
    raise cException("%s could not be contacted (error: %s)" % (sURLNameInException, repr(oException)));
  uStatusCode = oHTTPRequest.getcode();
  sData = oHTTPRequest.read();
  if uStatusCode == 404:
    raise cException("%s was not found (HTTP 404)." % sURLNameInException);
  if uStatusCode >= 500:
    raise cException("%s returned an internal error code %03d." % (sURLNameInException, uStatusCode));
  if uStatusCode != 200:
    raise cException("%s returned an unexpected response code %03d." % (sURLNameInException, uStatusCode));
  if not sData:
    raise cException("%s did not return any data." % sURLNameInException);
  return sData;

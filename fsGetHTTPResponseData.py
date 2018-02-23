import ssl, urllib, urlparse;
from .dsCertificateFilePath_by_sHostname import dsCertificateFilePath_by_sHostname;

def fsGetHTTPResponseData(sURL, sPostData, cException):
  oURL = urlparse.urlparse(sURL);
  if oURL.scheme == "https":
    sCertificateFilePath = dsCertificateFilePath_by_sHostname.get(oURL.hostname);
    if sCertificateFilePath:
      # For use with site-pinning.
      oSSLContext = ssl.create_default_context(cafile = sCertificateFilePath);
    else:
      oSSLContext = ssl.create_default_context();
      oSSLContext.load_default_certs();
  try:
    oHTTPRequest = urllib.urlopen(sURL, sPostData, context = oSSLContext);
  except Exception as oException:
    raise cException("The server could not be contacted (error: %s)" % repr(oException));
  uStatusCode = oHTTPRequest.getcode();
  sData = oHTTPRequest.read();
  if uStatusCode == 404:
    raise cException("The server url was not found (HTTP 404).");
  if uStatusCode > 500:
    raise cException("The server returned error code %03d." % uStatusCode);
  if uStatusCode != 200:
    raise cException("The server provided an unexpected response code %03d." % uStatusCode);
  if not sData:
    raise cException("The server response does not contain any data.");
  return sData;

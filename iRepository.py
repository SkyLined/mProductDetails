class iRepository(object):
  sType = None;
  sb0RepositoryURL = None;
  sb0ProductDetailsJSONURL = None;
  sb0LatestVersionZipURL = None;
  
  def foGetLatestProductDetails(oSelf):
    assert oSelf.sb0ProductDetailsJSONURL is not None, \
        "Cannot get latest product details because sb0ProductDetailsJSONURL is None";
    return cProductDetails.foConstructFromJSONString(
      sbJSON = fsbGetHTTPResponseData(
        sbURL = oSelf.sb0ProductDetailsJSONURL,
        sURLNameInException = "The product details in the %s repository at %s" % (oSelf.__class__.sType, str(oSelf.sb0RepositoryURL, "ascii", "strict")),
      ),
      sDataNameInError = str(oSelf.sb0ProductDetailsJSONURL, "ascii", "strict")
    );
  
  def fsGetLatestVersionZipFileContent(oSelf):
    assert oSelf.sb0LatestVersionZipURL is not None, \
        "Cannot get latest product version zip file content because sb0LatestVersionZipURL is None";
    return fsbGetHTTPResponseData(
      sbURL = oSelf.sb0LatestVersionZipURL,
      sURLNameInException = "The latest product version .zip file in the %s repository at %s" % (oSelf.__class__.sType, str(oSelf.sb0RepositoryURL, "ascii", "strict")),
    );

from .cProductDetails import cProductDetails;
from .fsbGetHTTPResponseData import fsbGetHTTPResponseData;
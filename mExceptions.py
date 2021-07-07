
class cProductDetailsException(Exception):
  def __init__(oSelf, sMessage, dxDetails):
    oSelf.sMessage = sMessage;
    oSelf.dxDetails = dxDetails;
    Exception.__init__(oSelf, sMessage, dxDetails);
  
  def __repr__(oSelf):
    return "<%s %s>" % (oSelf.__class__.__name__, oSelf);
  def __str__(oSelf):
    sDetails = ", ".join("%s: %s" % (str(sName), repr(xValue)) for (sName, xValue) in oSelf.dxDetails.items());
    return "%s (%s)" % (oSelf.sMessage, sDetails);

class cServerResponseException(cProductDetailsException):
  pass;

class cJSONDataException(cProductDetailsException):
  pass;
class cJSONDataSyntaxException(cJSONDataException):
  pass;
class cJSONDataVersionException(cJSONDataException):
  pass;
class cJSONDataTypeException(cJSONDataException):
  pass;

class cLicenseSyntaxErrorException(cProductDetailsException):
  pass;
class cErrorException(Exception):
  def __init__(oSelf, sMessage):
    super(cErrorException, oSelf).__init__(sMessage);
    oSelf.sMessage = sMessage;
  def __str__(oSelf):
    return oSelf.sMessage;
  def __repr__(oSelf):
    return "%s(%s)" % (oSelf.__class__.__name__, oSelf.sMessage);

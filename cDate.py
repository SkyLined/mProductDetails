import datetime, re;

### cDate ###
grDate = re.compile(r"^(\d{4})[\-\/](\d{1,2})[\-\/](\d{1,2})$");
class cDate(datetime.date):
  @staticmethod
  def foNow():
    oNow = datetime.datetime.utcnow();
    return cDate(oNow.year, oNow.month, oNow.day);
  @staticmethod
  def foFromString(sDate):
    oDateMatch = grDate.match(sDate);
    return oDateMatch and cDate(*[long(s) for s in oDateMatch.groups()]);
  
  def foEndDateForDuration(oSelf, sDuration):
    oDurationMatch = re.match(r"(\d+)([ymd])", sDuration.lower());
    assert oDurationMatch, \
        "Invalid duration %s" % sDuration;
    (sCount, sType) = oDurationMatch.groups();
    uCount = long(sCount);
    oEndDate = cDate(oSelf.year, oSelf.month, oSelf.day);
    if sType == "y":
      oEndDate = oEndDate.replace(year = oEndDate.year + uCount);
    elif sType == "m":
      if oEndDate.month == 12:
        oEndDate = oEndDate.replace(year = oEndDate.year + 1, month = 1);
      else:
        oEndDate = oEndDate.replace(month = oEndDate.month + 1);
    elif sType == "d":
      oEndDate += datetime.timedelta(days = 1);
    else:
      raise AssertionError("NOT REACHED");  
    return oEndDate;
  
  def __str__(oSelf):
    return oSelf.isoformat();

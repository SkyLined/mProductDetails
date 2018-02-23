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
    oEndDate = cDate(oSelf.year, oSelf.month, oSelf.day);
    for sDurationComponent in sDuration.split("+"):
      oDurationComponentMatch = re.match(r"(\d+)([ymd])", sDurationComponent.lower());
      assert oDurationComponentMatch, \
          "Invalid duration %s" % sDuration;
      (sCount, sType) = oDurationComponentMatch.groups();
      uCount = long(sCount);
      if sType == "y":
        oEndDate = oEndDate.replace(year = oEndDate.year + uCount);
      elif sType == "m":
        uNewMonth = oEndDate.month + uCount;
        while uNewMonth > 12:
          oEndDate = oEndDate.replace(year = oEndDate.year + 1);
          uNewMonth -= 12;
        oEndDate = oEndDate.replace(month = uNewMonth);
      elif sType == "d":
        oEndDate += datetime.timedelta(days = uCount);
      else:
        raise AssertionError("NOT REACHED");  
    return oEndDate;
  
  def __str__(oSelf):
    return oSelf.isoformat();

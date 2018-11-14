import datetime, re;

### cDate ###
grDate = re.compile(r"^(\d{4})[\-\/](\d{1,2})[\-\/](\d{1,2})$");
grDurationComponent = re.compile(r"^(\d+)([ymd])$");
gasMonths = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];
gasOrdinalPostfixes = [
  "th", "st", "nd", "rd", "th", "th", "th", "th", "th", "th"
];
class cDate(datetime.date):
  @property
  def uYear(oSelf):
    return oSelf.year;
  @uYear.setter
  def uYear(oSelf, uYear):
    oSelf.year = uYear;
  
  @property
  def uMonth(oSelf):
    return oSelf.month;
  @uMonth.setter
  def uMonth(oSelf, uMonth):
    oSelf.month = uMonth;
  
  @property
  def uDay(oSelf):
    return oSelf.day;
  @uDay.setter
  def uDay(oSelf, uDay):
    oSelf.day = uDay;
  
  @staticmethod
  def foNow():
    oNow = datetime.datetime.utcnow();
    return cDate(oNow.year, oNow.month, oNow.day);
  @staticmethod
  def foFromString(sDate):
    oDateMatch = grDate.match(sDate);
    return oDateMatch and cDate(*[long(s) for s in oDateMatch.groups()]);
  
  def foEndDateForDuration(oSelf, sDuration):
    oEndDate = cDate(oSelf.uYear, oSelf.uMonth, oSelf.uDay);
    for sDurationComponent in sDuration.split("+"):
      oDurationComponentMatch = re.match(grDurationComponent, sDurationComponent.lower());
      assert oDurationComponentMatch, \
          "Invalid duration %s" % sDuration;
      (sCount, sType) = oDurationComponentMatch.groups();
      uCount = long(sCount);
      if sType == "y":
        oEndDate = oEndDate.replace(year = oEndDate.uYear + uCount);
      elif sType == "m":
        uNewMonth = oEndDate.uMonth + uCount;
        while uNewMonth > 12:
          oEndDate = oEndDate.replace(year = oEndDate.uYear + 1);
          uNewMonth -= 12;
        # If we try to go from the 31st of any month to a month that has 30 days or less by replacing only the month,
        # we would end up on a day that does not exist. Attempting to do so causes a ValueError, in which case we
        # decrease the day by one and try again. We may need to do this a number of times in case of February. This
        # gets us a date with the month changed by the desired value and the day adjusted to most closely match the
        # original value and still be valid.
        while 1:
          try:
            oEndDate = oEndDate.replace(month = uNewMonth);
          except ValueError:
            oEndDate = oEndDate.replace(day = oEndDate.uDay - 1);
          else:
            break;
      elif sType == "d":
        oEndDate += datetime.timedelta(days = uCount);
      else:
        raise AssertionError("NOT REACHED");  
    return oEndDate;
  
  def fsToHumanReadableString(oSelf):
    # Month <day>th, <year>
    return "%s %d%s, %d" % (
      gasMonths[oSelf.uMonth],
      oSelf.uDay, gasOrdinalPostfixes[oSelf.uDay % 10],
      oSelf.uYear,
    );
  
  def __str__(oSelf):
    return oSelf.isoformat();

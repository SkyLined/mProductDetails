import datetime, re;

### cVersion ###
grVersion = re.compile(r"^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})$");
class cVersion(object):
  @staticmethod
  def foNew():
    oNow = datetime.datetime.utcnow();
    return cVersion(oNow.year, oNow.month, oNow.day, oNow.hour, oNow.minute);
  @staticmethod
  def foFromString(sVersion):
    oVersionMatch = grVersion.match(sVersion);
    if oVersionMatch is None: return None;
    return cVersion(*[long(s) for s in oVersionMatch.groups()]);
  def __init__(oSelf, uYear, uMonth, uDay, uHour, uMinute):
    assert uYear is not None, \
        "uYear cannot be None";
    assert uMonth is not None, \
        "uMonth cannot be None";
    assert uDay is not None, \
        "uDay cannot be None";
    assert uHour is not None, \
        "uHour cannot be None";
    assert uMinute is not None, \
        "uMinute cannot be None";
    oSelf.uYear = uYear;
    oSelf.uMonth = uMonth;
    oSelf.uDay = uDay;
    oSelf.uHour = uHour;
    oSelf.uMinute = uMinute;
  
  @property
  def __uComparableValue(oSelf):
    return (
      (
        (
          (
            (
              oSelf.uYear, 
            ) * 12 + oSelf.uMonth
          ) * 31 + oSelf.uDay
        ) * 24 + oSelf.uHour
      ) * 60 + oSelf.uMinute
    );
  
  def __eq__(oSelf, oVersion):
    if oVersion.__class__ != cVersion: return NotImplemented;
    return oSelf.__uComparableValue == oVersion.__uComparableValue;
  def __ge__(oSelf, oVersion):
    if oVersion.__class__ != cVersion: return NotImplemented;
    return oSelf.__uComparableValue >= oVersion.__uComparableValue;
  def __gt__(oSelf, oVersion):
    if oVersion.__class__ != cVersion: return NotImplemented;
    return oSelf.__uComparableValue > oVersion.__uComparableValue;
  def __le__(oSelf, oVersion):
    return not oSelf.__gt__(oVersion);
  def __lt__(oSelf, oVersion):
    return not oSelf.__ge__(oVersion);
  def __ne__(oSelf, oVersion):
    return not oSelf.__eq__(oVersion);
  def __str__(oSelf):
    return "%04d-%02d-%02d %02d:%02d" % (oSelf.uYear, oSelf.uMonth, oSelf.uDay, oSelf.uHour, oSelf.uMinute);


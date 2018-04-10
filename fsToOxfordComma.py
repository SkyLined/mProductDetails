def fsToOxfordComma(asValues):
  if len(asValues) == 1:
    return asValues[0];
  return (
    ", ".join(asValues[:-1])
    + (len(asValues) > 2 and "," or "")
    + " and " + asValues[-1]
  );

if __name__ == "__main__":
  def fCheck(asInput, sExpectedOutput):
    sOutput = fsToOxfordComma(asInput);
    assert sExpectedOutput == sOutput, \
        "Input %s did not produce output %s but %s" % (repr(asInput), repr(sExpectedOutput), repr(sOutput));
  fCheck(["One"],                         "One");
  fCheck(["One", "Two"],                  "One and Two");
  fCheck(["One", "Two", "Three"],         "One, Two, and Three");
  fCheck(["One", "Two", "Three", "Four"], "One, Two, Three, and Four");
  
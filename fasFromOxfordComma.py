def fasFromOxfordComma(sValues):                          # "One"      || "One and Two"           || "One, Two, and Three"
  asValues = sValues.split(", ");                         # ["One"]    || ["One and Two"]         || ["One", "Two", "and Three"]
  asLastValues = asValues.pop().split(" ");               #   ["One"]  ||   ["One", "and", "Two"] ||   ["and", "Three"]
  if (len(asLastValues) > 1):
    asLastValues = asLastValues[:-2] + asLastValues[-1:]  #                 ["One", "Two"]        ||   ["Three"]
  return asValues + asLastValues;                         # ["One"]    || ["One", "Two"]          ||  ["One", "Two", "Three"]

if __name__ == "__main__":
  def fCheck(sInput, asExpectedOutput):
    asOutput = fasFromOxfordComma(sInput);
    assert asExpectedOutput == asOutput, \
        "Input %s did not produce output %s but %s" % (repr(sInput), repr(asExpectedOutput), repr(asOutput));
  fCheck("One",                         ["One"]);
  fCheck("One and Two",                 ["One", "Two"]);
  fCheck("One, Two, and Three",         ["One", "Two", "Three"]);
  fCheck("One, Two, Three, and Four",   ["One", "Two", "Three", "Four"]);
  
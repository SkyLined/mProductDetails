import random;
print("sLicenseConfigurationId: %s" % "".join( ["%02X" % random.randrange(0x100) for x in range(12)] ));

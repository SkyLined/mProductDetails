import hashlib, os, uuid;
from mRegistry import cRegistryValue;

def fsHKLMValue(sKeyPath, sValueName):
  oRegistryValue = cRegistryValue.foGet(sHiveName = "HKLM", sKeyPath = sKeyPath, sValueName = sValueName);
  if not oRegistryValue:
    oRegistryValue = cRegistryValue.foGet(sHiveName = "HKLM", sKeyPath = sKeyPath, sValueName = sValueName, uRegistryBits = 64);
    assert oRegistryValue, \
        "Cannot read HKLM\%s\%s" % (sKeyPath, sValueName);
  assert oRegistryValue.sTypeName == "REG_SZ", \
      r"Expected HKLM\%s\%s to be REG_SZ, got %s" % (sKeyPath, sValueName, oRegistryValue.sTypeName);
  return oRegistryValue.xValue;

# Generate a unique system id. We want this to be a value that is unique to this machine and user account. The server
# uses these ids to track the different machines and user accounts that the product has been actived on in order to
# enforce the limits on the number of instances set in the license. We only need the id to be unique and unchanging for
# this machine and user. It should not contain any recoverable data as that would constitute an information leak.
# We will construct this id by first taking values that, when combined, should provide our uniqueness requirements and
# not change between reboots. The values used are:
#
# * A unique machine id found in the Windows Registry that is set at installation. This is large enough to be unique
#   for the Windows install, but if a VM is cloned after installing Windows, there will be multiple machines with the
#   same "unique" machine id, so it is not enough to uniquely identify the machine by itself.
# * The MAC address of one of the network interfaces. This is unique to the hardware card in case of a physical machine
#   or the virtual switch in case of a VM. However, Python may not be able to determine the MAC addresses, so it cannot
#   be used stand-alone. Also, MAC addresses can be spoofed and people tend to choose easy to remember values,
#   potentially leading to collisions between different machines, so it is not entirely guaranteed to be unique by
#   itself.
# * The machine name as found in the Windows Registry, which is used to identify it on the local network. This is
#   entirely under the user's control, so collisions are very likely.
# * The name of the logged in user as set in the "USERNAME" environment variable. This is guaranteed to be different
#   for different user accounts on the same system.
#
# The above values combined will be passed through a secure hash function to construct a similarly unique id which does
# not allow recovery of the original values used to construct it. 

uMAC = uuid.getnode(); 
# If Python cannot determine the real MAC address, it will return a random value with the 8th bit set.
if (uMAC & 0x030000000000): 
  # If this is the case, we'll leave it out, as otherwise the unique id would change between different runs.
  uMAC = 0;

asUniqueValues = [
  fsHKLMValue(r"SOFTWARE\Microsoft\Cryptography", "MachineGuid"),  # Windows installation id gathered from the registry
  "%X" % uMAC,                  # MAC address gather from one of the network interfaces.
  fsHKLMValue(r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName", "ComputerName"), # Machine name gathered from the registry
  os.getenv("USERNAME"),        # User name gathered from the environment.
];

gsSystemId = hashlib.sha256("".join(asUniqueValues).encode("utf-8")).hexdigest()[:32];           # Limit to 32 characters.

def fsGetSystemId():
  return gsSystemId;

import hashlib, os;
from mWindowsAPI import oSystemInfo;

# Generate a unique system id. We want this to be a value that is unique to this OS install and user account, so
# the server can use it to track on how many machines the product is actived by a user, as this may be limited by
# the license. However, the value should not leak any information about the machine or the user to the server.
# Windows provides a unique machine id and user name that we can use, but these must be procesed to obscure the
# information they qould otherwise convey. Hashing these values should practically guarantee a unique id that does
# not provide any information about the machine or the user to the server.
gsSystemId = hashlib.sha256(oSystemInfo.sUniqueSystemId + str(os.getenv("USERNAME"))).hexdigest();

def fsGetSystemId():
  return gsSystemId;

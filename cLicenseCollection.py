# Local imports are at the end to prevent import loops.
import mFileSystem;

class cLicenseCollection(object):
  # A license collection is a list of licenses which offers some convenience functions to import and export them, check
  # them with the Windows registry and/or a server, get a valid&active license for a product, or a list of errors that
  # explain why there is no valid&active license for a product.
  @staticmethod
  def foReadFromFile(sLicenseFilePath, sProductName = None):
    sLicenseBlocks = mFileSystem.fsReadDataFromFile(sLicenseFilePath);
    return cLicenseCollection.foFromLicenseBlocks(sLicenseBlocks, sProductName = sProductName);
    
  @staticmethod
  def foFromLicenseBlocks(sLicenseBlocks, sProductName = None):
    aoLicenses = cLicense.faoForLicenseBlocks(sLicenseBlocks, sProductName = sProductName)
    return aoLicenses and cLicenseCollection(aoLicenses) or None;
  
  def __init__(oSelf, aoLicenses):
    oSelf.aoLicenses = aoLicenses;
  
  def fCheckWithRegistryOrServer(oSelf, oLicenseCheckServer):
    for oLicense in oSelf.aoLicenses:
      oLicense.fCheckWithRegistryOrServer(oLicenseCheckServer);
  
  def fCheckWithServer(oSelf, oLicenseCheckServer, bWriteToRegistry = True):
    for oLicense in oSelf.aoLicenses:
      oLicense.fCheckWithServer(oLicenseCheckServer, bWriteToRegistry = bWriteToRegistry);
  
  def foGetLicenseForProductName(oSelf, sProductName):
    # Get the first active, valid, non-revoked licenses for this product that has not exceeded its allowed instances:
    for oLicense in oSelf.aoLicenses:
      if (
        oLicense.sProductName == sProductName
        and oLicense.bIsActive
        and oLicense.bIsValid
        and not oLicense.bIsRevoked
        and not oLicense.bLicenseInstancesExceeded
      ):
        return oLicense;
      
  def fasGetErrors(oSelf, sProductName = None):
    # Get a description of the problems for all licenses for this product. Returns an empty array if at least one
    # license is active, valid, and non-revoked and has not exceeded its allowed instances:
    if len(oSelf.aoLicenses) == 0:
      return ["You have no license."];
    asErrors = [];
    for oLicense in oSelf.aoLicenses:
      if sProductName in [None, oLicense.sProductName]:
        if oLicense.bIsExpired:
          asErrors.append("You have a license with id %s that expired on %s." % (oLicense.sLicenseId, oLicense.oEndDate));
        elif not oLicense.bIsActive:
          asErrors.append("You have a license with id %s that activates on %s." % (oLicense.sLicenseId, oLicense.oStartDate));
        elif oLicense.bIsValid:
          asErrors.append("You have a license with id %s that is not valid." % oLicense.sLicenseId);
        elif oLicense.bIsRevoked:
          asErrors.append("You have a license with id %s that is revoked." % oLicense.sLicenseId);
        elif oLicense.bLicenseInstancesExceeded:
          asErrors.append("You have a license with id %s that has exceeded its instances." % oLicense.sLicenseId);
        else:
          # There is a active, valid, non-revoked licenses for this product that has not exceeded its allowed instances:
          return []; # return no errors for this product.
    # All licenses for this product had a problem, or there were no licenses for this product.
    return asErrors;
  
  @property
  def sLicenseBlocks(oSelf):
    return "\r\n".join([oLicense.sLicenseBlock for oLicense in oSelf.aoLicenses]);

from .cLicense import cLicense;
from .cLicenseCheckServer import cLicenseCheckServer;

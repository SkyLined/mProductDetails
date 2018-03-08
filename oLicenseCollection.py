# The imports are at the end to prevent import loops.
class cLicenseCollection(object):
  # A license collection is a list of licenses which offers some convenience functions to import and export them, check
  # them with the Windows registry and/or a server, get a valid&active license for a product, or a list of errors that
  # explain why there is no valid&active license for a product.
  def __init__(oSelf, aoLicenses = []):
    oSelf.aoLicenses = aoLicenses;

  def faoAddLicenses(oSelf, aoLicenses):
    # Add only licenses that are different from those in the collection:
    aoAddedLicenses = [];
    for oNewLicense in aoLicenses:
      for oExistingLicense in oSelf.aoLicenses:
        if oNewLicense.sLicenseBlock == oExistingLicense.sLicenseBlock:
          break;
      else:
        aoAddedLicenses.append(oNewLicense);
        oSelf.aoLicenses.append(oNewLicense);
    return aoAddedLicenses;
  
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
      
  def fasGetErrors(oSelf, sProductName):
    # Get a description of the problems for all licenses for this product. Returns an empty array if at least one
    # license is active, valid, and non-revoked and has not exceeded its allowed instances:
    if len(oSelf.aoLicenses) == 0:
      return ["You have no license for %s." % sProductName];
    asErrors = [];
    for oLicense in oSelf.aoLicenses:
      if sProductName in oLicense.sProductName:
        if oLicense.bIsExpired:
          asErrors.append("Your license for %s with id %s expired on %s." % \
              (sProductName, oLicense.sLicenseId, oLicense.oEndDate));
        elif not oLicense.bIsActive:
          asErrors.append("Your license for %s with id %s activates on %s." % \
              (sProductName, oLicense.sLicenseId, oLicense.oStartDate));
        elif oLicense.bIsValid:
          asErrors.append("Your license for %s with id %s is not valid." % \
              (sProductName, oLicense.sLicenseId));
        elif oLicense.bIsRevoked:
          asErrors.append("Your license for %s with id %s has been revoked." % \
              (sProductName, oLicense.sLicenseId));
        elif oLicense.bLicenseInstancesExceeded:
          asErrors.append("Your license for %s with id %s has exceeded its maximum number of instances." % \
              (sProductName, oLicense.sLicenseId));
        else:
          # There is a active, valid, non-revoked licenses for this product that has not exceeded its allowed instances:
          return []; # return no errors for this product.
    # All licenses for this product had a problem, or there were no licenses for this product.
    return asErrors;
  
  @property
  def sLicenseBlocks(oSelf):
    return "\r\n".join([oLicense.sLicenseBlock for oLicense in oSelf.aoLicenses]);

from .cLicense import cLicense;
from .cLicenseCheckRegistry import cLicenseCheckRegistry;
from .cLicenseCheckServer import cLicenseCheckServer;
import mFileSystem;

# Create a license colllection with all license stored in the registry
oLicenseCollection = cLicenseCollection();
oLicenseCollection.faoAddLicenses(cLicenseCheckRegistry.faoReadLicensesFromRegistry());

import __main__;
from .cProductDetails import cProductDetails;

def fo0GetProductDetailsForModule(mModule):
  # Load and return product details for the provided module (if it has them).
  return cProductDetails.fo0GetForModule(mModule);

import __main__;
from .cProductDetails import cProductDetails;

def foGetProductDetailsForModule(mModule):
  # Load and return product details for the provided module (if it has them).
  return cProductDetails.foGetForModule(mModule);

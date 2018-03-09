import __main__;
from .cProductDetails import cProductDetails;

def foGetProductDetailsForMainModule():
  # Load and return product details for the main module (if it has them).
  return cProductDetails.foGetForModule(__main__);

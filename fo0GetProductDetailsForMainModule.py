import __main__;
from .cProductDetails import cProductDetails;

def fo0GetProductDetailsForMainModule():
  # Load and return product details for the main module (if it has them).
  return cProductDetails.fo0GetForModule(__main__);

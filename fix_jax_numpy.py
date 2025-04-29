#!/usr/bin/env python3
"""
JAX-NumPy Compatibility Fix

This module patches NumPy to add a 'dtypes' attribute that JAX expects.
This resolves the AttributeError: module 'numpy' has no attribute 'dtypes'
that occurs when JAX and TensorFlow are used together with certain versions.
"""

import numpy as np
import sys
import warnings

def apply_jax_numpy_fix():
    """
    Patch NumPy to add the expected 'dtypes' attribute when JAX tries to access it.
    
    This works around the error:
    AttributeError: module 'numpy' has no attribute 'dtypes'
    """
    if not hasattr(np, 'dtypes'):
        # Create a simple class that will be used as np.dtypes
        class DummyStringDType:
            pass
            
        class DTypesNamespace:
            def __init__(self):
                self.StringDType = DummyStringDType
                
        # Patch numpy with the dtypes namespace
        np.dtypes = DTypesNamespace()
        
        # Suppress specific JAX warnings that might occur
        try:
            warnings.filterwarnings('ignore', message='.*JAX on Windows.*')
            warnings.filterwarnings('ignore', message='.*TensorFlow and JAX.*')
        except:
            pass
            
        print("Applied JAX-NumPy compatibility patch")
    
    return True

# Allow this file to be run directly to apply the fix
if __name__ == "__main__":
    apply_jax_numpy_fix()
    print("JAX-NumPy compatibility patch has been applied")
    sys.exit(0)
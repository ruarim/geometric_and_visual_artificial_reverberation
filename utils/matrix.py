from scipy.linalg import hadamard
import numpy as np
from math import sqrt

def householder(n):
    v = np.random.randn(n)
    v /= np.linalg.norm(v)
    H = np.eye(n) - 2 * np.outer(v, v)
    return H

def scaled_hadamard(N):
    """
    Hadamard matrix scaled to the square root of the matrix size.
    """
    return hadamard(N) / sqrt(N)
    

# does this NEED to be a class ?
# class Matrix:
#     def __init__(self, M):
#         self.hardamard = hadamard(M)
    
    # hadarmard 

    # isotropic

    # householder

    # diagonal

    # unitary interpolation
    
    # BRDF
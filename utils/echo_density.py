import numpy as np
from utils.matlab import init_matlab_eng

def echo_density(rir, fs, truncate=True):
    # truncate to first non zero sample to remove predelay
    if truncate:
        none_zero = np.argmax(rir != 0.0)
        rir = rir[none_zero:]
    
    matlab_eng = init_matlab_eng()
    
    rir_T = rir[..., None] # np.atleast_2d(rir).T
    
    # call fdn toolbox 
    t_mix, ed = matlab_eng.echoDensity(rir_T, 1024, fs, 0, nargout=2)
    matlab_eng.quit()
    
    ed = np.array(ed)[0]
    
    return ed
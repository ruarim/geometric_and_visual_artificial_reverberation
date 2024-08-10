import numpy as np
from utils.matlab import init_matlab_eng

def echo_density(rir, fs, truncate=True):
    # truncate to first non zero sample to remove predelay
    if truncate:
        none_zero = np.argmax(rir != 0)
        rir = rir[none_zero:]
    
    matlab_eng = init_matlab_eng()
    
    # call fdn toolbox 
    ed = np.array(matlab_eng.echoDensity(rir, 1024, fs, 0))
    
    matlab_eng.quit()
    
    return ed[0]
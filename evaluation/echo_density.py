import numpy as np
from utils.matlab import init_matlab_eng
from matplotlib import pyplot as plt

def echo_density(rir, fs, truncate=False, plot=False, name=''):
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
    
    if plot:
        # time_vec = np.arange(len(rir)) // (fs)
        plt.figure(figsize=(10, 4))
        plt.title(f'Echo Density: {name}')
        plt.plot(rir, label='RIR')
        plt.plot(ed, 'r.', markersize=2, label='Echo Density')
        plt.xlabel('Samples')
        plt.legend()
    
    return ed
import numpy as np
from matplotlib import pyplot as plt

def echo_density(rir, fs, matlab_eng, truncate_start=False, plot=False, name='', len_secs=0.25, ref_ed=[], ref_tmix=0):
    # truncate to first non zero sample to remove predelay
    if truncate_start:
        none_zero = np.argmax(rir != 0.0)
        rir = rir[none_zero:]
        
    rir_T = rir[..., None] # np.atleast_2d(rir).T
    
    # call fdn toolbox 
    t_mix, ed = matlab_eng.echoDensity(rir_T, 1024, fs, 0, nargout=2)
    
    ed = np.array(ed)[0]
    ed = np.where(np.isfinite(ed), ed, 0)
    
    t_mix = np.argmax(ed >= 1.0)
    
    if plot:
        plot_lim = int(len_secs * fs)
        t_mix_sec = t_mix / fs
        rir = rir[:plot_lim]
        ed = ed[:plot_lim]
        time_vec = np.arange(len(rir)) / (fs)
        plt.figure(figsize=(10, 4))
        plt.title(f'Echo Density: {name}')
        plt.plot(time_vec, rir)
        plt.plot(time_vec, ed,  label=f'{name} Echo Density')
        if len(ref_ed) > 0: plt.plot(time_vec, ref_ed, label='Real Echo Density')
        plt.xlabel('Time (secs)')
        plt.ylabel('Amplitude and Similarity to Gaussian Noise')
        plt.axvline(x=t_mix_sec, color='b', linestyle='--', linewidth=2, label=f'{name} Mixing Time {round(t_mix_sec, 3)} secs')
        if ref_tmix != 0: plt.axvline(x=ref_tmix / fs, color='r', linestyle='--', linewidth=2, label=f'Real Mixing Time {round(ref_tmix / fs, 3)} secs')
        plt.legend()
        plt.xlim([0, plot_lim / fs])
        plt.ylim([np.min(rir) * 1.05, np.max(ed) * 1.05])
    
    return ed, t_mix
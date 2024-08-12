import numpy as np
from matplotlib import pyplot as plt
from librosa import power_to_db

def modal_density(h, fs, band=-1, rt60=1, plot=False, name=''):
    magnitude_spectrum = np.abs(np.fft.fft(h))

    # only consider the first half of the spectrum (positive frequencies)
    frequencies = np.fft.fftfreq(len(h), d=1/fs)
    positive_freq_indices = np.where(frequencies >= 0)
    magnitude_spectrum = magnitude_spectrum[positive_freq_indices]
    magnitude_spectrum = power_to_db(magnitude_spectrum ** 2, ref=np.max)
    frequencies = frequencies[positive_freq_indices]
    
    if band != -1:
        # define the octave band range
        lower_bound = band / np.sqrt(2)
        upper_bound = band * np.sqrt(2)
        
        # filter frequencies for the 500 Hz octave band
        band_indices = np.where((frequencies >= lower_bound) & (frequencies <= upper_bound))

        # filtered frequency and magnitude spectrum
        frequencies = frequencies[band_indices]
        magnitude_spectrum = magnitude_spectrum[band_indices]
       
    peaks = []
    for i in range(len(frequencies)):
        if i > 0 and i < len(frequencies) - 1:
            curr = {
                'amplitude': magnitude_spectrum[i],
                'freq': frequencies[i]
            }
            prev = {
                'amplitude': magnitude_spectrum[i - 1],
                'freq': frequencies[i - 1]
            }
            next = {
                'amplitude': magnitude_spectrum[i + 1],
                'freq': frequencies[i + 1]
            }
            peak = parabolic_peak_pick(
                curr,
                prev,
                next,
            )
            
            if peak != None:
                peaks.append(peak)
    
    peak_freq = [freq[0] for freq in peaks]
    peak_amp = [amp[1] for amp in peaks]
        
    num_peaks = len(peaks)
    frequency_range = frequencies[-1] - frequencies[0]
    modal_density = num_peaks / frequency_range
    is_shroeder_min, min_modes = shroeder_min(frequency_range, num_peaks, rt60)
    
    if plot:    
        plt.figure(figsize=(10, 4))
        plt.title(f'Modal Density {name}: Density: {round(modal_density, 3)}, Modes: {num_peaks}, Shroeder Min Modes: {round(min_modes, 3)}')
        plt.plot(frequencies, magnitude_spectrum, label='Magnitude Spectrum')
        plt.plot(peak_freq, peak_amp, 'r.', markersize=3, label='Peaks')
        plt.legend()
    
    return num_peaks, modal_density, is_shroeder_min

def parabolic_peak_pick(curr, prev, next, threshold=-40):
    """
    Spectral peak picking via parabolic interpolation.
    https://ccrma.stanford.edu/~jos/sasp/Peak_Detection_Steps_3.html
    
    Frequencies tend to be about twice as accurate when dB magnitude is used 
    rather than just linear magnitude.
    
    Parameters:
    - curr: dict with keys 'freq' and 'amplitude'
    - prev: dict with keys 'freq' and 'amplitude'
    - next: dict with keys 'freq' and 'amplitude'
    - threshold: Minimum amplitude (in dB) to consider a peak significant
    
    Returns:
    - A dictionary containing 'peak_frequency' and 'peak_amplitude' if a peak is found,
      or None if no peak is found.
    """
    
    if(
      curr['amplitude'] > prev['amplitude'] and 
      curr['amplitude'] > next['amplitude'] and 
      curr['amplitude'] > threshold
    ):
        bin = (0.5 * (prev['amplitude'] - next['amplitude'])) / (prev['amplitude'] - 2.0 * curr['amplitude'] + next['amplitude'])
        
        peak_freq = curr['freq'] + 0.5 * (next['freq'] - prev['freq']) * bin
        peak_amp  = curr['amplitude'] - 0.25 * (prev['amplitude'] - next['amplitude']) * bin
        peak = [ 
            peak_freq,
            peak_amp,
        ]
        
        return peak
    
def shroeder_min(frequnecy_resolution, num_modes, rt60):
    """
    Schroeder's formula for minimum number of modes.
    Colorless artificial reverberation (M. R. Schroeder and B. F. Logan, 1961) 
    """
    min_density = (0.15 * rt60 * frequnecy_resolution)
    return  num_modes >= min_density, min_density
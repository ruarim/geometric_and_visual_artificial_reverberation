import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin2, freqz, minimum_phase
from librosa import power_to_db

from .convolve import fft_convolution
from .plot import plot_spectrogram

def fir_type_1(freqs, gains, nyquist, numtaps=201):
    """
    Create an FIR filter with frequnecy response fit to frequency bands and gains
    DC and Nyquist gains extraploated from maximum and minimum indexes of gains.
    """
    assert len(freqs) == len(gains)
    assert freqs[-1] < nyquist
    assert numtaps % 2 != 0
    normalized_freqs = np.concatenate(([0], freqs / nyquist, [1]))
    gains_min = gains[0]
    gains_max = gains[-1]
    gains = np.concatenate(([gains_min], gains, [gains_max])) # repeat the first and last gain for the full spectrum
    numtaps = 201 
    linear_fir = firwin2(numtaps, normalized_freqs, gains)
    min_fir = minimum_phase(linear_fir)
    return linear_fir, min_fir
    
def fir_type_2(freqs, gains, nyquist, numtaps=200):
    """
    Create an FIR filter with frequnecy response fit to frequency bands and gains
    Gain 1 at DC and 0 at nyquist
    """
    assert len(freqs) == len(gains)
    assert freqs[-1] < nyquist
    assert numtaps % 2 == 0
    normalized_freqs = np.concatenate(([0], freqs / nyquist, [1]))
    gains = np.concatenate(([1], gains, [0])) # repeat the first and last gain for the full spectrum
    linear_fir = firwin2(numtaps, normalized_freqs, gains)
    min_fir = minimum_phase(linear_fir, method='hilbert')
    return linear_fir, min_fir

def plot_fir(x, freqs, gains, fs, db=False, y_scale='linear'):
    nyquist = fs / 2
    
    # make filters
    fir_coeffs_1, fir_coeff_1_min = fir_type_1(freqs, gains, nyquist)
    fir_coeffs_2, fir_coeff_2_min = fir_type_2(freqs, gains, nyquist)

    # Plot the frequency response
    w_1, h_1 = freqz(fir_coeffs_1, worN=fs)
    h_1 =  abs(h_1)
    w_2, h_2 = freqz(fir_coeffs_2, worN=fs)
    h_2 =  abs(h_2)

    w_1_min, h_1_min = freqz(fir_coeff_1_min, worN=fs)
    h_1_min =  abs(h_1_min)

    w_2_min, h_2_min = freqz(fir_coeff_2_min, worN=fs)
    h_2_min = abs(h_2_min)
    
    # to dB
    if db:
        gains = power_to_db(gains**2)
        h_1 = power_to_db(h_1**2)
        h_2 = power_to_db(h_2**2)
        h_1_min = power_to_db(h_1_min**2)
        h_2_min = power_to_db(h_2_min**2)
    
    plt.figure(figsize=(10, 4))
    plt.title("FIR Frequency Response vs Desired Attenuation at bands")
    plt.xscale('log')
    plt.xticks(freqs, labels=[str(band) for band in freqs])
    # plt.xlim([freqs[0] - (freqs[0] / 2), nyquist + 1000])
    # plt.xlim([freqs[0], nyquist])
    plt.plot(w_1 * nyquist / np.pi, h_1, label=f'FIR Type I Order: {len(fir_coeffs_1) - 1}')
    plt.plot(w_2 * nyquist / np.pi, h_2, label=f'FIR Type II Order: {len(fir_coeffs_2) - 1}')
    plt.plot(w_1_min * nyquist / np.pi, h_1_min, label=f'FIR Type I Minimum-Phase Order: {len(fir_coeff_1_min) - 1}')
    plt.plot(w_2_min * nyquist / np.pi, h_2_min, label=f'FIR Type II Minimum-Phase Order: {len(fir_coeff_2_min) - 1}')
    plt.plot(freqs, gains, "o", label='Desired')
    plt.xlabel('Frequency (Hz)')
    if db: 
        plt.ylim([-30, 1])
        plt.ylabel('Gain (dB)')
    else: plt.ylabel('Gain (Linear)')
    plt.legend()
    plt.grid()
    
    y = np.zeros_like(x)
    y = fft_convolution(x, fir_coeffs_1, y)
    plt.figure(figsize=(10,4))
    plt.plot(x, label='Input')
    plt.plot(y, label='Output')
    plt.legend()
    plot_spectrogram(y, sr=fs, y_scale=y_scale, title='FIR Output Spectogram')
    plot_spectrogram(x, sr=fs, y_scale=y_scale, title='Input Spectrogram')
    
    y = np.zeros_like(x)
    y = fft_convolution(x, fir_coeffs_2, y)
    plt.figure(figsize=(10,4))
    plt.plot(x, label='Input')
    plt.plot(y, label='Output')
    plt.legend()
    plot_spectrogram(y, sr=fs, y_scale=y_scale, title='FIR Output Spectogram')
    plot_spectrogram(x, sr=fs, y_scale=y_scale, title='Input Spectrogram')
    
    plt.show()
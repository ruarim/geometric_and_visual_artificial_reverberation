import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin2, freqz, minimum_phase
from librosa import power_to_db

def fir_type_1(freqs, gains, nyquist, numtaps=201):
    """
    Create an FIR filter with frequnecy response fit to frequency bands and gains
    DC and Nyquist gains extraploated from maximum and minimum indexes of gains.
    """
    assert numtaps % 2 != 0
    normalized_freqs = np.concatenate(([0], np.array(freqs) / nyquist, [1]))    
    gains = np.array([gains[0]] + gains + [gains[-1]])  # repeat the first and last gain for the full spectrum
    numtaps = 201 
    linear_fir = firwin2(numtaps, normalized_freqs, gains)
    min_fir = minimum_phase(linear_fir)
    return linear_fir, min_fir
    
def fir_type_2(freqs, gains, nyquist, numtaps=200):
    """
    Create an FIR filter with frequnecy response fit to frequency bands and gains
    Gain 1 at DC and 0 at nyquist
    """
    assert numtaps % 2 == 0
    normalized_freqs = np.concatenate(([0], np.array(freqs) / nyquist, [1]))
    gains = np.array([1] + gains + [0])  # repeat the first and last gain for the full spectrum
    linear_fir = firwin2(numtaps, normalized_freqs, gains)
    min_fir = minimum_phase(linear_fir, method='hilbert')
    return linear_fir, min_fir 

def get_fir_coeffs(freqs, gains, fs, plot=False):
    nyquist = fs / 2
    
    assert len(freqs) == len(gains)
    assert freqs[-1] < nyquist
    
    # get alpha from absorption coeffs
    gains = [1 - a for a in gains]

    # make filters
    fir_coeffs_1, fir_coeff_1_min = fir_type_1(freqs, gains, nyquist)
    fir_coeffs_2, fir_coeff_2_min = fir_type_2(freqs, gains, nyquist)

    # Plot the frequency response
    w_1, h_1 = freqz(fir_coeffs_1, worN=fs)
    h_1 =  abs(h_1) # take real numbers

    w_2, h_2 = freqz(fir_coeffs_2, worN=fs)
    h_2 =  abs(h_2) # take real numbers

    w_1_min, h_1_min = freqz(fir_coeff_1_min, worN=fs)
    h_1_min =  abs(h_1_min) # take real numbers

    w_2_min, h_2_min = freqz(fir_coeff_2_min, worN=fs)
    h_2_min =  abs(h_2_min) # take real numbers

    if plot:
        # to dB
        # h = power_to_db(h**2)
        # gains = power_to_db(gains**2)
        plt.figure(figsize=(10, 4))
        plt.title("FIR Frequency Response vs Desired Attenuation at bands")
        plt.xscale('log')
        plt.xticks(freqs, labels=[str(band) for band in freqs])
        # plt.xlim([freqs[0] - (freqs[0] / 2), freqs[-1] + (freqs[-1] / 2)])
        # plt.xlim([freqs[0], freqs[-1]])
        plt.plot(w_1 * nyquist / np.pi, h_1, label='FIR Type I')
        plt.plot(w_2 * nyquist / np.pi, h_2, label='FIR Type II')
        plt.plot(w_1_min * nyquist / np.pi, h_1_min, label='FIR Type I Minimum-Phase')
        plt.plot(w_2_min * nyquist / np.pi, h_2_min, label='FIR Type II Minimum-Phase')
        plt.plot(freqs, gains, label='Desired')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Gain (dB)')
        plt.legend()
        plt.grid()
        plt.show()


# frequency bands and attenuation values
freqs = [125, 250, 500, 1000, 2000, 4000, 8000]
gains = [0.07, 0.31, 0.49, 0.81, 0.66, 0.54, 0.48]
fs = 44100

get_fir_coeffs(freqs, gains, fs, plot=True)
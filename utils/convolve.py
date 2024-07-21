import numpy as np
from scipy.fft import fft, ifft

def fft_convolution(input_signal, rir, output_signal):
    # Find the next power of two for zero-padding (for efficient FFT computation)
    n = len(input_signal) + len(rir) - 1
    N = 2 ** np.ceil(np.log2(n)).astype(int)

    # Compute the FFT of both signals
    fft_audio = fft(input_signal, N)
    fft_ir = fft(rir, N)

    # Perform the convolution in the frequency domain
    fft_convolution = fft_audio * fft_ir

    # Compute the inverse FFT to get the time domain signal
    convolved_signal = ifft(fft_convolution)

    # Retain only the real part
    convolved_signal = np.real(convolved_signal)

    # Normalize the convolved signal to prevent clippin
    # convolved_signal = convolved_signal / np.max(np.abs(convolved_signal))
    
    # output signal in the correct shape
    return convolved_signal
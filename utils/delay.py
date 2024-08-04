import numpy as np
from utils.fractional_delay import fractional_delay
from scipy.signal import lfilter

class DelayLine:
    """
    Sample by sample processing delay line
    """
    def __init__(self, size):
        self.size = size
        self.buffer = np.zeros(size + 1)
        self.index = 0

    def push(self, value: float):
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size

    def read(self, delay: int):
        assert delay < self.size, "Delay exceeds buffer size"
        read_index = (self.index - delay - 1) % self.size
        return self.buffer[read_index]
    
def delay_array(x, delay, fs, frac_filter_N=81):
    """
    Delay an array via zero padding
    """
    output_signal = np.zeros_like(x)
    
    delay_int = int(delay * fs)
    delay_frac = (fs * delay) - delay_int
    # apply integer delay
    delayed_signal = np.pad(x, (delay_int, 0), 'constant')[:len(x)]
    # apply fractional delay
    frac_filter = fractional_delay(delay_frac, N=frac_filter_N)
    fractional_delayed_signal = np.convolve(delayed_signal, frac_filter, mode='same')
                    
    return fractional_delayed_signal[:len(output_signal)]

class TappedDelayLine:
    def __init__(self, delays, gains, filter_coeffs, fs, frac_filter_N=81, use_filter=True):
        self.delays = delays  # delay times in seconds
        self.gains = gains  # gain values for each delay
        self.fs = fs
        self.filter_coeffs = filter_coeffs
        self.use_filter = use_filter
        self.frac_filter_N = frac_filter_N
        self.group_delay = (frac_filter_N - 1) // 2

    def process(self, input_signal, output_signal):        
        for delay, gain, filter_coeffs in zip(self.delays, self.gains, self.filter_coeffs):
            delay_int = int(delay * self.fs)
            delay_frac = (self.fs * delay) - delay_int
            # apply integer delay
            delayed_signal = np.pad(input_signal, (delay_int, 0), 'constant')[:len(input_signal)]
            # apply fractional delay
            frac_filter = fractional_delay(delay_frac, N=self.frac_filter_N)
            fractional_delayed_signal = np.convolve(delayed_signal, frac_filter, mode='same')
            
            # correct for the group delay of the fractional delay filter
            # fractional_delayed_signal = np.concatenate(
            #     (np.zeros(self.group_delay), fractional_delayed_signal)
            # )
            
            if(self.use_filter): fractional_delayed_signal = lfilter(filter_coeffs, [1], fractional_delayed_signal)
            output_signal += (gain * fractional_delayed_signal)
        
        return output_signal[:len(output_signal)]



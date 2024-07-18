import numpy as np
from utils.fractional_delay import fractional_delay

class TappedDelayLine:
    def __init__(self, delays, gains, fs, frac_filter_N=81):
        self.delays = delays  # delay times in seconds
        self.gains = gains  # gain values for each delay
        self.fs = fs
        self.frac_filter_N = frac_filter_N
        self.group_delay = (frac_filter_N - 1) // 2

    def process(self, input_signal, output_signal):        
        for delay, gain in zip(self.delays, self.gains):
            delay_int = int(delay * self.fs)
            delay_frac = (self.fs * delay) - delay_int
            # apply integer delay
            delayed_signal = np.pad(input_signal, (delay_int, 0), 'constant')[:len(input_signal)]
            # apply fractional delay
            frac_filter = fractional_delay(delay_frac, N=self.frac_filter_N)
            fractional_delayed_signal = np.convolve(delayed_signal, frac_filter, mode='same')
            # correct for the group delay of the fractional delay filter
            corrected_signal = np.concatenate(
                (np.zeros(self.group_delay), fractional_delayed_signal)
            )[:len(output_signal)]
            
            output_signal += (gain * corrected_signal) # pass alpha array
            
        return output_signal
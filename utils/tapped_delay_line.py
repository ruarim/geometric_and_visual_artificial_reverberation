import numpy as np

class TappedDelayLine:
    def __init__(self, delays, gains, fs):
        self.delays = delays  # Delay times in seconds
        self.gains = gains  # Gain values for each delay
        self.fs = fs  # Sampling frequency
        self.delay_samples = [int(d * fs) for d in delays]

    def process(self, input_signal, output_signal):
        for delay, gain in zip(self.delay_samples, self.gains):
            delayed_signal = np.pad(input_signal, (delay, 0), 'constant')[:len(input_signal)]
            output_signal += gain * delayed_signal
        return output_signal
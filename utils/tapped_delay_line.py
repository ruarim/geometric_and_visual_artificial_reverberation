import numpy as np

class TappedDelayLine:
    def __init__(self, delays, gains, fs):
        self.delays = delays  # Delay times in seconds
        self.gains = gains  # Gain values for each delay
        self.fs = fs  # Sampling frequency
        self.delay_samples = [int(d * fs) for d in delays]

    def process(self, input_signal):
        # simplify this code
        output_signal = np.zeros_like(input_signal)
        for delay, gain in zip(self.delay_samples, self.gains):
            delayed_signal = np.pad(input_signal, (delay, 0), 'constant')[:len(input_signal)]
            output_signal += gain * delayed_signal
        return output_signal
    
    def tap_in():
        pass
    
    def tap_out():
        pass

# Example usage
fs = 44100  # Sampling frequency
delays = [0.002, 0.005, 0.009]  # Delays in seconds
gains = [0.5, 0.3, 0.2]  # Gains for each delay

input_signal = np.array([...])  # Replace with actual input signal
tdl = TappedDelayLine(delays, gains, fs)
output_signal = tdl.process(input_signal)

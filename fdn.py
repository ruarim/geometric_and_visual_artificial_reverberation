import numpy as np

from utils.delay_line import DelayLine

class FeedbackDelayNetwork:
    def __init__(self, b, c, matrix, delay_times, fs, rt60_flat, rt60_bands=[], lossless=False):
        self.fs = fs
        self.b = b
        self.c = c
        self.matrix = matrix
        self.rt60_flat = rt60_flat
        print(rt60_flat)
        self.rt60_bands = rt60_bands
        self.lossless = lossless
        self.delay_times = delay_times
        self.delays = self._make_delays()
        self.feedback_gain = self._make_feedback_gain()
        # self.feedback_filters = self._make_feedback_filters()
    
    # // internal methods //
    
    # perform vector matrix multiplication
    # this function `should` be implemented differently for certain matrices
    # for example isotropic is a very simple nest for loop with a single multiply
    # for simplicity use standard vector matrix multiplication, with no optimisation at first
    # A scalar multiplication is performed between the output vector of the delay lines and the nth row of the feedback matrix - (diva phd)
    def _apply_matrix(self, x):
        return np.dot(self.matrix, x) # self.matrix @ x also might work
    
    # filter vector of samples
    def _apply_rt60_filters(self):
        pass
    
    # takes vector of samples
    def _delays_in(self, samples):
        for delay, sample in zip(self.delays, samples):
            delay.push(sample)
    
    # return vector of samples
    def _delays_out(self):
        return [delay.read(time) for delay, time in zip(self.delays, self.delay_times)]
    
    def _make_feedback_filters(self, rt60_bands):
        pass
    
    def _make_delays(self):
        return [DelayLine(time + 1) for time in self.delay_times]
    
    def _make_feedback_gain(self): # TODO: Fix, values to close to 1.0
        gain_db = -60 * (1/self.fs * self.rt60_flat)
        print(gain_db)
        gain_linear = pow(10, gain_db / 20)
        print(gain_linear)
        return gain_linear
    
    # // periphery methods //
    def process(self, x):  
        # tap out from delay
        delay_out = self._delays_out()
        
        # # apply filter
        if(not self.lossless):
            # add conditional for bands or flat
            delay_out = [sample * self.feedback_gain for sample in delay_out]
        
        # apply mixing matrix
        delays_mixed = self._apply_matrix(delay_out)
        
        # combine input and feedback samples
        network_in = (delays_mixed + x) # / 2.0 ?
        
        # tap in to delay
        self._delays_in(network_in * self.b)
        
        # apply c
        y = delay_out * self.c
        
        # sum output vector
        return np.sum(y)
    
    def plot():
        pass
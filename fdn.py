class FDN:
    def __init__(self, M, b, c, matrix, delays, rt60_bands):
        self.M = M
        self.b = b
        self.c = c
        self.matrix = matrix
        self.delays = delays
        self.rt60_bands = rt60_bands
        self.filters = self._make_filters()
    
    # // internal methods //
    
    # perform vector matrix multiplication
    # this function `should` be implemented differently for certain matrices
    # for example isotropic is a very simple nest for loop with a single multiply
    # for simplicity use standard vector matrix multiplication, with no optimisation at first
    # A scalar multiplication is performed between the output vector of the delay lines and the nth row of the feedback matrix - (diva phd)
    def _apply_matrix(self):
        pass
    
    # filter vector of samples
    def _apply_filters(self):
        pass
    
    # takes vector of samples
    def _delays_in(self):
        pass
    
    # return vector of samples
    def _delays_out(self):
        pass
    
    def _make_filters(self, rt60_bands):
        pass
    
    # // periphery methods //
    
    #
    def process(self, x):
        # apply b
        y = x * self.b 
        
        # tap out from delay
        
        # apply filter
        
        # apply matrix
        
        # tap in to delay
        
        # apply c
        
        return y
    
    def plot():
        pass
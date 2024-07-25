import numpy as np
from math import sqrt

from utils.point3D import Point3D
from .source import Source
from .mic import Mic

class ScatteringJunction:    
    # add arg types
    def __init__(self, location: Point3D, source: Source, mic: Mic, alpha=1.0):
        self.propigation_in = []
        self.propigation_out = []
        self.location = location
        self.source = source
        self.mic = mic
        self.absorption = sqrt(1-alpha)
        
        # wall filter
    
    # get the sample from neigbour junctions
    # output an array of scattered values
    def scatter_in(self, source_sample):
        # get reflection order
        M = len(self.propigation_out)
        # scale source
        source_sample_scaled = source_sample * 0.5
        # read samples in from neighbours
        samples_in = [s.sample_out() for s in self.propigation_in]
        # output samples
        sample_to_mic = 0.0
        samples_out = np.zeros(M)
        
        for i in range(M): # output prop lines
            sample_out = 0.0
            for j in range(M): # input prop lines
                sample_in = samples_in[j] + source_sample_scaled
                # isotropic scattering coefficient
                if i == j: a = 2 / M - 1.0 # less to diagonal
                else: a = 2 / M
                
                sample_out += sample_in * a
                            
            # filter sample (frequnecy dependant absorption) and attenuation (non frequency dependant absorption)
            
            # to neighbour junctions
            samples_out[i] = sample_out * self.absorption
                       
            # to mic prop line
            sample_to_mic += (2/M)*sample_out
                    
        return samples_out, sample_to_mic
    
    def scatter_out(self, samples):
        M = len(self.propigation_out)
        assert len(samples) == M
        for i in range(M):
            self.propigation_out[i].sample_in(samples[i])
    
    def add_in(self, prop_in):
        self.propigation_in.append(prop_in)
        
    def add_out(self, prop_out):
        self.propigation_out.append(prop_out)
        
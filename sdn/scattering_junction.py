import numpy as np
from math import sqrt
from scipy.signal import lfilter, lfilter_zi, lfiltic

from utils.point3D import Point3D
from .source import Source
from .mic import Mic

class ScatteringJunction:    
    # add arg types
    def __init__(self, location: Point3D, source: Source, mic: Mic, alpha=1.0, filter_coeffs=None):
        self.propigation_in = []
        self.propigation_out = []
        self.location = location
        self.source = source
        self.mic = mic
        self.absorption = sqrt(1-alpha)
        self.wall_filter_numer = filter_coeffs
        self.wall_filter_denom = [1.0]
        self.wall_filter_zi = np.zeros(len(self.wall_filter_numer) - 1)
        # self.wall_filter_zi = lfiltic(self.wall_filter_numer, self.wall_filter_denom, [0]) # for IIR or lfilter_zi
    
    # get the sample from neigbour junctions
    # output an array of scattered values
    def scatter_in(self, source_sample):
        # get reflection order
        M = len(self.propigation_out)
        # scale source
        source_sample_scaled = source_sample * 0.5
        # read samples in from neighbours
        samples_in = [prop_line.sample_out() for prop_line in self.propigation_in]
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
                
            # create output to neighbour junctions
            if self.absorption != 0:
                samples_out[i] = sample_out * self.absorption #frequency independant absorption
            else:
                filter_out, zf = lfilter(self.wall_filter_numer, self.wall_filter_denom, [sample_out], zi=self.wall_filter_zi)# samples_out[i] =  #frequnecy dependant absorption
                self.wall_filter_zi = zf
                samples_out[i] = filter_out[0]

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
        
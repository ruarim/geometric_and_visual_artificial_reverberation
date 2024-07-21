import numpy as np

from utils.point3D import Point3D
from utils.tapped_delay_line import TappedDelayLine
from utils.geometry import euclid_dist, distance_to_delay
from utils.convolve import fft_convolution
from config import SimulationConfig, RoomConfig

class EarlyReflections:
    def __init__(self, source: Point3D, mic: Point3D, image_sources: list[Point3D], image_source_walls: list[str], sim_config: SimulationConfig, room_config: RoomConfig, ism_rir):
        self.fs = sim_config.FS
        self.c = sim_config.SPEED_OF_SOUND
        self.source = source
        self.mic = mic
        self.image_sources = image_sources
        self.image_source_walls = image_source_walls
        self.wall_absorption = room_config.WALL_ABSORPTION

        # rendered image source method RIR
        self.ism_rir = ism_rir
        
        # get delay times from 3D points
        self.delay_times = self._make_delay_times()
        
        # attenuation over distance (1/r law)
        distance_attenuation = self._make_distance_attenuation()
        wall_attenuation_flat = self._make_wall_attenuation_flat()
        
        self.attenuation = distance_attenuation * wall_attenuation_flat
        
        # TODO - add wall attenuation gain / filter at each output
        self.tapped_delay_line = TappedDelayLine(self.delay_times, self.attenuation, self.fs) # inject tdl instead
        
        # self.scattering_network = ScatteringNetwork()
    
    # TODO also return direct sound in a seperate array
    def process(self, input_signal, output_signal, type: str):
        """
        Render the early reflections
        
        Returns: delayed and attenuated samples (numpy array)
        """
        if type == 'tdl': return self.tapped_delay_line.process(input_signal, output_signal)
        if type == 'convolve': return fft_convolution(input_signal, self.ism_rir, output_signal)
        if type == 'scattering': print('scattering')
        
        # apply frequnecy dependant decay filter bank - only for tapped delay line
        
    
    def _make_delay_times(self):
        return [self._point_to_delay_time(self.mic, image_source) for image_source in self.image_sources]
    
    def _make_distance_attenuation(self):
        return np.array([self._point_to_attenuation(self.mic, image_source) for image_source in self.image_sources])
    
    def _make_wall_attenuation_flat(self):
        return np.array([(1.0 - self.wall_absorption[wall]) for wall in self.image_source_walls])
        
    def _make_wall_filter(self):
        # run IIR optimisation - instead output to file
        pass
        
    def _point_to_delay_time(self, mic, point):
        distance = euclid_dist(point, mic)
        delay = distance_to_delay(distance, self.c)
        return delay
    
    def _point_to_attenuation(self, mic, point):
        distance = euclid_dist(point, mic)
        return min(1 / distance, 1)
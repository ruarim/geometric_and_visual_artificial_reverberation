import numpy as np
from scipy.fft import fft, ifft

from utils.point3D import Point3D
from utils.tapped_delay_line import TappedDelayLine
from utils.geometry import euclid_dist, distance_to_delay
from utils.convolve import freq_domain_convolution
from config import SimulationConfig, RoomConfig

class EarlyReflections:
    def __init__(self, source: Point3D, mic: Point3D, reflection_points: list[Point3D], sim_config: SimulationConfig, room_config: RoomConfig, ism_rir):
        self.fs = sim_config.FS
        self.c = sim_config.SPEED_OF_SOUND
        self.source = source
        self.mic = mic
        self.reflection_points = reflection_points
        self.wall_absorption = room_config.WALL_ABSORPTION

        # rendered image source method response
        self.ism_rir = ism_rir
        # ism_order ??
        
        # get delay times from 3D points
        self.delay_times = self._make_delay_times()
        
        # attenuation over distance (1/r law)
        distance_attenuation = self._make_attenuation()
        # distance_attenuation = np.ones_like(self.delay_times)
        
        # TODO - add wall attenuation gain / filter at each output
        self.tapped_delay_line = TappedDelayLine(self.delay_times, distance_attenuation, self.fs) # inject tdl instead
        
        # self.scattering_network = ScatteringNetwork()
    
    def process(self, input_signal, output_signal, type: str):
        """
        Render the early reflections
        
        Returns: delayed and attenuated samples (numpy array)
        """
        if type == 'tdl': return self.tapped_delay_line.process(input_signal, output_signal)
        if type == 'convolve': return freq_domain_convolution(input_signal, self.ism_rir, output_signal)
        if type == 'scattering': print('scattering')
    
    def _make_delay_times(self):
        return [self._point_to_delay_time(self.mic, point) for point in self.reflection_points]
    
    def _make_attenuation(self):
        return [self._point_to_attenuation(self.mic, point) for point in self.reflection_points]
        
    def _point_to_delay_time(self, mic, point):
        distance = euclid_dist(point, mic)
        delay = distance_to_delay(distance, self.c)
        return delay
    
    def _point_to_attenuation(self, mic, point):
        distance = euclid_dist(point, mic)
        return min(1 / distance, 1)       
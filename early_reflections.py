import numpy as np

from utils.point3D import Point3D
from utils.tapped_delay_line import TappedDelayLine
from utils.geometry import euclid_dist, distance_to_delay
from config import SimulationConfig

class EarlyReflections:
    def __init__(self, source: Point3D, mic: Point3D, reflection_points: list[Point3D], config: SimulationConfig):
        self.fs = config.FS
        self.c = config.SPEED_OF_SOUND
        self.source = source
        self.mic = mic
        self.reflection_points = reflection_points
        
        # get delay times from 3D points
        delay_times = [self.point_to_delay(mic, point) for point in reflection_points]
        
        # attenuation over distance (1/r law)
        distance_attenuation = [self.point_to_attenuation(mic, point) for point in reflection_points]
        
        self.tapped_delay_line = TappedDelayLine(delay_times, distance_attenuation, self.fs)
        
        # self.scattering_network = ScatteringNetwork()
    
    def process(self, input_signal, output_signal, type: str):
        """
        Render the early reflections
        
        Returns: delayed and attenuated samples (numpy array)
        """
        if type == 'tdl': return self.tapped_delay_line.process(input_signal, output_signal)
        if type == 'scattering': print('scattering')
        
    def point_to_delay(self, mic, point):
        distance = euclid_dist(point, mic)
        delay = distance_to_delay(distance, self.c)
        return delay
    
    def point_to_attenuation(self, mic, point):
        distance = euclid_dist(point, mic)
        return min(1 / distance, 1)
       
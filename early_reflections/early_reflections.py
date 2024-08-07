import numpy as np

from utils.point3D import Point3D
from utils.delay import TappedDelayLine
from utils.delay import delay_array
from utils.geometry import euclid_dist, distance_to_delay
from utils.convolve import fft_convolution
from utils.filters import fir_type_1, fir_type_2
from config import SimulationConfig, RoomConfig

class EarlyReflections:
    def __init__(self, source: Point3D, mic: Point3D, image_sources: list[Point3D], image_source_walls: list[str], sim_config: SimulationConfig, room_config: RoomConfig, ism_rir, wall_center_freqs, material_absorption, material_filter=True, fir_type="I"):
        self.fs = sim_config.FS
        self.c = sim_config.SPEED_OF_SOUND
        self.source = source
        self.mic = mic
        self.image_sources = image_sources
        self.image_source_walls = image_source_walls
        self.wall_absorption_flat = room_config.WALL_ABSORPTION
        self.wall_absorption_bands = material_absorption
        self.wall_center_freqs = wall_center_freqs
        self.fir_type = fir_type

        # rendered image source method RIR
        self.ism_rir = ism_rir
        
        # get delay times from 3D points
        self.delay_times = self._make_early_reflection_delay_times()
        
        # attenuation over distance (1/r law)
        distance_attenuation = self._make_distance_attenuation()
        wall_attenuation_flat = self._make_wall_attenuation_flat()
        
        if not material_filter: self.distance_attenuation = distance_attenuation + wall_attenuation_flat
        
        self.distance_attenuation = distance_attenuation
        self.wall_filter_coeffs = self._make_wall_filters()
        
        self.direct_delay = self._point_to_delay_time(self.mic, self.source)
        
        self.tapped_delay_line = TappedDelayLine(self.delay_times, self.distance_attenuation, self.wall_filter_coeffs, self.fs, use_filter=material_filter)
            
    # TODO also return direct sound in a seperate array
    def process(self, input_signal, output_signal, type: str):
        """
        Render the early reflections
        
        Returns: delayed and attenuated samples (numpy array)
        """
        direct = delay_array(input_signal, self.direct_delay, self.fs)
        
        if type == 'tdl': 
            er = self.tapped_delay_line.process(input_signal)
        if type == 'convolve':
            er = fft_convolution(input_signal, self.ism_rir)
        if type == 'multi-channel':
            er = np.array([delay_array(input_signal, d, self.fs) * gain for d, gain in zip(self.delay_times, self.distance_attenuation)])
        
        return er, direct
                
    def _make_early_reflection_delay_times(self):
        return [self._point_to_delay_time(self.mic, image_source) for image_source in self.image_sources]
    
    def _make_distance_attenuation(self):
        return np.array([self._point_to_attenuation(self.mic, image_source) for image_source in self.image_sources])
    
    def _make_wall_attenuation_flat(self):
        return np.array([(1.0 - self.wall_absorption_flat[wall]) for wall in self.image_source_walls])
        
    def _make_wall_filters(self):
        nyquist = self.fs / 2
        return [self._make_filter(self.wall_center_freqs, self.wall_absorption_bands[wall], nyquist, self.fir_type) for wall in self.image_source_walls]
   
    @staticmethod
    def _make_filter(freqs, gains, nyquist, fir_type):
        if fir_type == "I": fir, fir_min = fir_type_1(freqs, 1 - np.array(gains), nyquist)
        if fir_type == "II": fir, fir_min = fir_type_2(freqs, 1 - np.array(gains), nyquist)
        return fir_min
    
    def _point_to_delay_time(self, mic, point):
        distance = euclid_dist(point, mic)
        delay = distance_to_delay(distance, self.c)
        return delay
    
    def _point_to_attenuation(self, mic, point):
        distance = euclid_dist(point, mic)
        return min(1 / distance, 1)
import numpy as np
from math import sqrt

from utils.matlab import init_matlab_eng
from config import SimulationConfig, RoomConfig
from early_reflections.ism import ImageSourceMethod
from early_reflections.early_reflections import EarlyReflections
from utils.point3D import Point3D
from utils.reverb_time import ReverbTime
from utils.absorption import Absorption
from utils.filters import tone_correction
from utils.primes import find_closest_primes, is_mutually_prime
from utils.delay import delay_array
from utils.plot import plot_comparison

class ISMFDN:
    def __init__(self, fs: float, simulation_config: SimulationConfig, room_config: RoomConfig, matlab_eng, fdn_N=-1, crossover_freq_multiple=4, processing_type='parallel', plot=False):
        self.matlab_eng = matlab_eng
        self.fs = fs
        self.fdn_N = fdn_N # TODO: From config
        self.crossover_freq_multiple = crossover_freq_multiple
        self.processing_type = processing_type
            
        # get the absoprtion coefficients at frequnecy bands for each wall
        self.absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, self.fs) # pass object
            
        self.absorption_coeffs = self.absorption.coefficients + self.absorption.air_absorption
        self.absorption_bands = self.absorption.freq_bands
        self.plot = plot
        if self.plot: self.absorption.plots_coefficients()
        
        # TODO: inject room details from room object
        reverb_time = ReverbTime(room_config)
        self.rt60_sabine, _ = reverb_time.theory_rt60s_bands(self.absorption_coeffs, self.absorption_bands, plot=plot)
        self.rt60_sabine_bands_500 = self.rt60_sabine[2]
        self.tranistion_frequency = reverb_time.transition_frequency(self.rt60_sabine_bands_500, multiple=self.crossover_freq_multiple)

        # find image sources up to Nth order 
        ism = ImageSourceMethod(room_config, fs=self.fs) # pass specific config values instead
        ism_er_rir = ism.process(norm=True) # rendering early reflections with pyroomacoustics ism
        image_source_coords, image_source_walls = ism.get_source_coords(plot=plot)
        image_source_points = [Point3D(image_source) for image_source in image_source_coords]
        source_point = Point3D(room_config.SOURCE_LOC)
        mic_point = Point3D(room_config.MIC_LOC)

        # tapped delay line or render ism and convolve with input
        self.early_reflections = EarlyReflections(
                source_point,  
                mic_point, 
                image_source_points,
                image_source_walls,
                simulation_config,
                room_config,
                ism_rir=ism_er_rir,
                wall_center_freqs=self.absorption_bands,
                material_absorption=self.absorption.coefficients_dict,
                material_filter=True
        )

        # delay from geometry
        self.fdn_delay_times = self.early_reflections.delay_times

        # use all image source delays
        if self.fdn_N == -1:
            self.fdn_N = len(self.fdn_delay_times)
        assert self.fdn_N <= len(self.fdn_delay_times), 'FDN order exceeds delays'

        # get closest primes to image source delay times
        self.fdn_delay_times = np.array([int(delay_sec * self.fs) for delay_sec in set(self.fdn_delay_times)])
        self.fdn_delay_times = find_closest_primes(self.fdn_delay_times)

        # if FDN order is power of two use a Hadamard otherwise use a random matrix
        is_power_2_N = self.is_power_of_2(self.fdn_N)
        if is_power_2_N:
                self.matrix_type = 'Hadamard' 
                # kth element sampling of delay times
                self.fdn_delay_times = np.sort(self.fdn_delay_times)
                k = len(self.fdn_delay_times) / self.fdn_N
                self.fdn_delay_times = np.array([self.fdn_delay_times[int(i * k)] for i in range(self.fdn_N)])
                    
        if not is_power_2_N:
                self.matrix_type = 'random'
            
        assert is_mutually_prime(self.fdn_delay_times), 'delays not mutually prime'

        # delay the input to the fdn by the shortest early reflection time
        sorted_times = np.sort(self.early_reflections.delay_times)
        self.first_er_delay = sorted_times[0]
                
        self.lr_fir_taps = 96
        self.lr_fir_group_delay = (self.lr_fir_taps // 2) / self.fs
        self.lr_fir_nyquist_decay_type = 'nyquist_zero'
        self.fdn_scaling_factor = 1 / sqrt(self.fdn_N)
        self.tone_correction_taps = 200

    def process(self, x, type=None):
        y = np.zeros_like(x)
        if type == None: type = self.processing_type
        
        print(f'ISMFDN: Processing {type}...')
        
        if type == 'serial': return self.process_serial(x, y)
        if type == 'parallel': return self.process_parallel(x, y)
        if type == 'fdn_only': return self.process_only_fdn(x)
            
    def process_only_fdn(self, x):               
        y =  self.matlab_eng.standard_fdn(
            self.fs,
            x * self.fdn_scaling_factor, 
            self.fdn_delay_times, 
            self.rt60_sabine
        )
        # end matlab process
        self.matlab_eng.quit()
        # mono
        y = np.array([t[0] for t in y])
        return y
        
    def process_parallel(self, x, y):
        er_tdl, direct_sound = self.early_reflections.process(x, y, type='tdl')
        

        lr_one_pole = self.matlab_eng.velvet_fdn_one_pole(
            self.fs, 
            x * self.fdn_scaling_factor, 
            self.fdn_delay_times, 
            self.rt60_sabine, 
            self.absorption_bands, 
            self.tranistion_frequency, 
            self.matrix_type
        )
        
        lr_fir      = self.matlab_eng.velvet_fdn_fir(
            self.fs, 
            x * self.fdn_scaling_factor, 
            self.fdn_delay_times, 
            self.rt60_sabine, 
            self.absorption_bands, 
            self.matrix_type,
            self.lr_fir_taps, 
            self.lr_fir_nyquist_decay_type
        )

        lr_one_pole = np.array([t[0] for t in lr_one_pole])
        lr_fir      = np.array([t[0] for t in lr_fir])

        # align late reverb with early reflections. 
        lr_one_pole = delay_array(lr_one_pole, self.first_er_delay, self.fs)
        lr_fir      = delay_array(lr_fir, self.first_er_delay - self.lr_fir_group_delay, self.fs)  

        lr_one_pole = tone_correction(
                lr_one_pole, 
                self.absorption_coeffs, 
                self.absorption_bands, 
                self.fs, 
                taps=self.tone_correction_taps, 
        )

        rir_one_pole = direct_sound + er_tdl + lr_one_pole
        rir_fir = direct_sound + er_tdl + lr_fir
        
        if self.plot:
            er_lr_compare = {
                'Late Reflections': lr_fir,
                'Early Reflections': er_tdl,
                'Direct Sound': direct_sound,
            }
            plot_comparison(er_lr_compare, title='Room Impulse Response', xlim=[0, 0.3])

        return rir_one_pole, rir_fir
          
    def process_serial(self, x, y):
        er_tdl,             direct_sound = self.early_reflections.process(x, y, type='tdl')
        er_signal_multi,    direct_sound = self.early_reflections.process(x, y, type='multi-channel')

        # apply FDN reverberation to output of early reflection stage
        lr_one_pole = self.matlab_eng.velvet_fdn_one_pole(
            self.fs, 
            er_tdl * self.fdn_scaling_factor, 
            self.fdn_delay_times, 
            self.rt60_sabine, 
            self.absorption_bands, 
            self.tranistion_frequency, 
            self.matrix_type
        )
        
        lr_one_pole_multi = self.matlab_eng.velvet_fdn_one_pole(
            self.fs, 
            er_signal_multi * self.fdn_scaling_factor, 
            self.fdn_delay_times, 
            self.rt60_sabine, 
            self.absorption_bands, 
            self.tranistion_frequency, 
            self.matrix_type
        )
        
        lr_fir = self.matlab_eng.velvet_fdn_fir(
            self.fs, 
            er_tdl * self.fdn_scaling_factor, 
            self.fdn_delay_times, 
            self.rt60_sabine, 
            self.absorption_bands, 
            self.matrix_type, 
            self.lr_fir_taps, 
            self.lr_fir_nyquist_decay_type
        )
        # mono
        lr_one_pole       = np.array([x[0] for x in lr_one_pole])
        lr_one_pole_multi = np.array([x[0] for x in lr_one_pole_multi])
        lr_fir            = np.array([x[0] for x in lr_fir])

        # tonal correction filter (gains = average of room absorption coefficients)
        filter_taps = 200
        lr_one_pole_tonal_correction = tone_correction(
                lr_one_pole, 
                self.absorption_coeffs, 
                self.absorption_bands, 
                self.fs, 
                taps=filter_taps, 
                plot=True
        )

        # combine direct sound, early and late reflections to create full RIRs
        one_pole_rir                  = direct_sound + er_tdl + lr_one_pole
        one_pole_mutli_rir            = direct_sound + np.sum(er_signal_multi, axis=0) + lr_one_pole_multi
        one_pole_tonal_correction_rir = direct_sound + er_tdl + lr_one_pole_tonal_correction
        fir_rir                       = direct_sound + er_tdl + lr_fir

        # TODO: return dict with name for plotting 
        return one_pole_tonal_correction_rir, fir_rir
        
    @staticmethod
    def is_power_of_2(n):
        """
        bitwise power of two check
        
        Returns (bool): power of two truth.
        """
        return n > 0 and (n & (n - 1)) == 0
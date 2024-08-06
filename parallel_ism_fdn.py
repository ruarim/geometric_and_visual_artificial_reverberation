import numpy as np
from matplotlib import pyplot as plt
from math import sqrt

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.matlab import init_matlab_eng
from utils.plot import plot_spectrogram, plot_comparison, plot_signal
from utils.signals import signal
from utils.reverb_time import ReverbTime
from utils.absorption import Absorption
from early_reflections.ism import ImageSourceMethod
from early_reflections.early_reflections import EarlyReflections
from utils.point3D import Point3D
from utils.file import write_array_to_wav
from utils.primes import find_log_mutual_primes, find_closest_primes, is_mutually_prime
from utils.delay import delay_array
from utils.filters import tone_correction

def is_power_of_2(n):
    return n > 0 and (n & (n - 1)) == 0

# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

fs = simulation_config.FS

# get the absoprtion coefficients at frequnecy bands for each wall
absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, fs)
absorption_coeffs = absorption.coefficients + absorption.air_absorption
absorption_bands = absorption.freq_bands
absorption.plots_coefficients()

reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s_bands(absorption_coeffs, absorption_bands, plot=True)
rt60_sabine_bands_500 = rt60_sabine[2]
rt60_eyring_bands_500 = rt60_eyring[2]
tranistion_frequency = reverb_time.transition_frequency(rt60_sabine_bands_500, multiple=2)

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config, fs=fs) # pass specific config values instead
ism_er_rir = ism.render(norm=True, order=2) # rendering early reflections with pyroomacoustics ism
image_source_coords, image_source_walls = ism.get_source_coords(show=False)
image_source_points = [Point3D(image_source) for image_source in image_source_coords]
source_point = Point3D(room_config.SOURCE_LOC)
mic_point = Point3D(room_config.MIC_LOC)

# tapped delay line or render ism and convolve with input
early_reflections = EarlyReflections(
        source_point,  
        mic_point, 
        image_source_points,
        image_source_walls,
        simulation_config,
        room_config,
        ism_rir=ism_er_rir,
        wall_center_freqs=absorption_bands,
        material_absorption=absorption.coefficients_dict,
        material_filter=True
)

# run acoustic simulation
input_signal, fs = signal(
        test_config.SIGNAL_TYPE, 
        simulation_config.SIGNAL_LENGTH, 
        fs, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
)

output_signal = np.zeros_like(input_signal)

er_tdl, direct_sound = early_reflections.process(input_signal, output_signal, type='tdl')
er_convolved, _ = early_reflections.process(input_signal, output_signal, type='convolve')

# delay from geometry
fdn_delay_times = early_reflections.delay_times
fdn_N = 16
# fdn_N = len(fdn_delay_times)

assert fdn_N <= len(fdn_delay_times), 'FDN order exceeds delays'

# get closest primes to image source delay times
fdn_delay_times = np.array([int(delay_sec * fs) for delay_sec in set(fdn_delay_times)])
fdn_delay_times = find_closest_primes(fdn_delay_times)

# if FDN order is power of two use a Hadamard otherwise use a random matrix
is_power_2_N = is_power_of_2(fdn_N)
if is_power_2_N:
        matrix_type = 'Hadamard' 
        # kth element sampling of delay times
        fdn_delay_times = np.sort(fdn_delay_times)
        k = len(fdn_delay_times) / fdn_N
        fdn_delay_times = np.array([fdn_delay_times[int(i * k)] for i in range(fdn_N)])
        
if not is_power_2_N:
        matrix_type = 'random'

print(f'FDN Delays: {fdn_delay_times}')
print(f'Delays mutually prime: {is_mutually_prime(fdn_delay_times)}')

# delay the input to the fdn by the shortest early reflection time
early_reflections.delay_times.sort()
# early_reflections.distance_attenuation.sort()
first_er_delay =  early_reflections.delay_times[0]
# first_er_gain  = early_reflections.distance_attenuation[0] # TODO: fix (smallest gain might not be first reflection)

lr_fir_filter_order = 96
lr_fir_group_delay = (lr_fir_filter_order // 2) / fs
scaling_factor = 1 / sqrt(fdn_N)

# start matlab process
matlab_eng = init_matlab_eng()

print('FDN: Processing late reverberation')

lr_one_pole = matlab_eng.velvet_fdn_one_pole(fs, input_signal * scaling_factor , fdn_delay_times, rt60_sabine, absorption_bands, tranistion_frequency, matrix_type)
lr_fir      = matlab_eng.velvet_fdn_fir(fs, input_signal * scaling_factor , fdn_delay_times, rt60_sabine, absorption_bands, matrix_type, lr_fir_filter_order)

lr_one_pole = np.array([t[0] for t in lr_one_pole])
lr_fir      = np.array([t[0] for t in lr_fir])

# align late reverb with early reflections. 
lr_one_pole = delay_array(lr_one_pole, first_er_delay, fs)
lr_fir      = delay_array(lr_fir, first_er_delay - lr_fir_group_delay, fs)  

filter_taps = 200
lr_one_pole = tone_correction(
        lr_one_pole, 
        absorption_coeffs, 
        absorption_bands, 
        fs, 
        taps=filter_taps, 
)

rir_one_pole = direct_sound + er_tdl + lr_one_pole
rir_fir = direct_sound + er_tdl + lr_fir

# end matlab process
matlab_eng.quit()

# normalise
# rir_one_pole /= abs(np.max(rir_one_pole))
# rir_fir /= abs(np.max(rir_fir))

config_str = f'Parallel ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

# write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str} One Pole", rir_one_pole, fs)
# write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str} FIR", rir_fir, fs)

spec_xlim = [0, 2]
wave_xlim = [0, 0.5]
compare = {
        'ER TDL': er_tdl,
        'LR One Pole': lr_one_pole,
        'LR FIR': lr_fir,
}

plot_signal(input_signal)
plot_spectrogram(rir_one_pole, fs, xlim=spec_xlim, title='rir_one_pole')
plot_spectrogram(rir_fir, fs, xlim=spec_xlim, title='rir_fir')
plot_comparison(compare, xlim=wave_xlim)
plot_signal(rir_fir,  xlim=wave_xlim, title='rir_fir')
plot_signal(rir_one_pole,  xlim=wave_xlim, title='rir_one_pole')
plt.show()
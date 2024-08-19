import numpy as np
from matplotlib import pyplot as plt
from pyroomacoustics.experimental.rt60 import measure_rt60
from math import sqrt

from utils.matlab import init_matlab_eng
from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from early_reflections.ism import ImageSourceMethod
from early_reflections.early_reflections import EarlyReflections
from utils.point3D import Point3D
from utils.signals import signal
from utils.plot import plot_comparison, plot_spectrogram, plot_signal
from utils.reverb_time import ReverbTime
from utils.file import write_array_to_wav
from utils.absorption import Absorption
from utils.filters import tone_correction
from utils.room import calc_mean_free_path
from utils.geometry import distance_to_delay
from utils.primes import find_log_mutual_primes, find_closest_primes, is_mutually_prime

# config dataclasses
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

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config, fs=fs) # pass specific config values instead
ism_er_rir = ism.process(norm=True) # rendering early reflections with pyroomacoustics ism
image_source_coords, image_source_walls = ism.get_source_coords(plot=False)
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

# TODO: inject room details from room object
reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s_bands(absorption_coeffs, absorption_bands, plot=True)
rt60_sabine_bands_500 = rt60_sabine[2]
rt60_eyring_bands_500 = rt60_eyring[2]
tranistion_frequency = reverb_time.transition_frequency(rt60_sabine_bands_500, multiple=4)

# TODO: use table instead
print(f'Center Frequnecies:       {absorption_bands}')
print(f'RT60 Bands Sabine:        {rt60_sabine}')
print(f'RT60 Bands Eyring:        {rt60_eyring}')
print(f'RT60 Bands Sabine 500 Hz: {rt60_sabine_bands_500}')
print(f'RT60 Bands Eyring 500 Hz: {rt60_eyring_bands_500}')
print(f'Transition Frequnecy:     {tranistion_frequency}')

mean_free_path = calc_mean_free_path(reverb_time.V, np.sum(reverb_time.S))
mean_free_path_delay = int(distance_to_delay(mean_free_path, simulation_config.SPEED_OF_SOUND) * (fs))

print(f'Mean Free Path Delay: {mean_free_path_delay}')
# delay from log mutual primes around mean free path
# fdn_order = 8
# log_mutal_primes = find_log_mutual_primes(mean_free_path_delay, fdn_order, percentage=75)
# fdn_delay_times = np.array(log_mutal_primes)


# delay from geometry
fdn_N = len(early_reflections.delay_times)
matrix_type = 'random' 
fdn_delay_times = np.array([int(delay_sec * fs) for delay_sec in set(early_reflections.delay_times)])
fdn_delay_times = find_closest_primes(fdn_delay_times)[:fdn_N]
print(f'FDN Delays: {fdn_delay_times}')
print(f'Delays mutually prime: {is_mutually_prime(fdn_delay_times)}')

# run acoustic simulation
input_signal, fs = signal(
        test_config.SIGNAL_TYPE, 
        simulation_config.SIGNAL_LENGTH, 
        fs, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
)
output_signal = np.zeros_like(input_signal)

print('TDL: processing early reflections')
er_tdl,             direct_sound = early_reflections.process(input_signal, output_signal, type='tdl')
er_signal_convolve, direct_sound = early_reflections.process(input_signal, output_signal, type='convolve')
er_signal_multi,    direct_sound = early_reflections.process(input_signal, output_signal, type='multi-channel')

lr_fir_filter_order = 96
lr_fir_nyquist_decay_type = "nyquist_zero"
scaling_factor = 1 / sqrt(len(fdn_delay_times))

# start matlab process
matlab_eng = init_matlab_eng()

# apply FDN reverberation to output of early reflection stage
print('FDN: one pole processing late reverberation')
lr_one_pole = matlab_eng.velvet_fdn_one_pole(fs, er_tdl * scaling_factor, fdn_delay_times, rt60_sabine, absorption_bands, tranistion_frequency, matrix_type)
print('FDN: one pole (MISO) processing late reverberation')
lr_one_pole_multi = matlab_eng.velvet_fdn_one_pole(fs, er_signal_multi * scaling_factor, fdn_delay_times, rt60_sabine, absorption_bands, tranistion_frequency, matrix_type)
print('FDN: FIR processing late reverberation')
lr_fir = matlab_eng.velvet_fdn_fir(fs, er_tdl * scaling_factor, fdn_delay_times, rt60_sabine, absorption_bands, matrix_type, lr_fir_filter_order, lr_fir_nyquist_decay_type)

# end matlab process
matlab_eng.quit()

# mono
lr_one_pole       = np.array([x[0] for x in lr_one_pole])
lr_one_pole_multi = np.array([x[0] for x in lr_one_pole_multi])
lr_fir            = np.array([x[0] for x in lr_fir])

# tonal correction filter (gains = average of room absorption coefficients)
filter_taps = 200
lr_one_pole_tonal_correction = tone_correction(
        lr_one_pole, 
        absorption_coeffs, 
        absorption_bands, 
        fs, 
        taps=filter_taps, 
        plot=True
)

# combine direct sound, early and late reflections to create full RIRs
one_pole_rir                  = direct_sound + er_tdl + lr_one_pole
one_pole_mutli_rir            = direct_sound + np.sum(er_signal_multi, axis=0) + lr_one_pole_multi
one_pole_tonal_correction_rir = direct_sound + er_tdl + lr_one_pole_tonal_correction
fir_rir                       = direct_sound + er_tdl + lr_fir

config_str = f'ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}_One-Pole", one_pole_rir, fs)
write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}_One-Pole_Tonal_Correction", one_pole_tonal_correction_rir, fs)    
write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}_FIR", fir_rir, fs)    

# render full rir for comparison
ism_order = 100
ism_rir = ism.process(order=ism_order)

# plot
compare_data = {
        "Full IMS": ism_rir / np.max(ism_rir),
        "Direct Sound": direct_sound,
        "Early ISM": ism_er_rir / np.max(ism_er_rir),
        "Early TDL": er_tdl,
        "FDN One-Pole": lr_one_pole,
        "FDN One-Pole Tonal Correction": lr_one_pole_tonal_correction,
        'FDN FIR': lr_fir,
        # 'FDN Multi (MISO)': ism_fdn_one_pole_mutli_rir,
}

xlim = [0, 2]

plot_signal(one_pole_mutli_rir, plot_time=True, title='FDN MISO')

# time plots comparison
plot_comparison(
        compare_data, 
        'ISM-FDN Comparison', 
        xlim=xlim, 
        plot_time=True,
        y_offset=0.0
)

# spectrograms
plot_spectrogram(ism_rir, fs, xlim=xlim, title="Spectrogram of ISM RIR")
plot_spectrogram(one_pole_rir, fs, xlim=xlim, title="Spectrogram of ISM-FDN (one-pole absorption) RIR")
plot_spectrogram(one_pole_tonal_correction_rir, fs, xlim=xlim, title="Spectrogram of ISM-FDN (one-pole absorption and Tonal Correction) RIR")
plot_spectrogram(fir_rir, fs, xlim=xlim, title="Spectrogram of ISM-FDN (FIR absorption) RIR")

comparison = {
        'one-pole fdn': lr_one_pole,
        'one-pole fdn (MISO)': lr_one_pole_multi,
        'Early Reflections Multi Channel': np.sum(er_signal_multi, axis=0)
        # 'one-pole tonal correction fdn': lr_signal_one_pole_tonal_correction,
        # 'fir fdn' : lr_signal_fir,
}
plot_comparison(comparison, xlim=xlim, plot_time=True)

# # RT60s
# plt.figure(figsize=(10, 4))
# plt.title('ISM RT60')
# measure_rt60(ism_rir, fs=fs, plot=True, rt60_tgt=rt60_sabine_bands_500)

# plt.figure(figsize=(10, 4))
# plt.title('ISM-FDN (one-pole) RT60')
# measure_rt60(one_pole_rir, fs=fs, plot=True, rt60_tgt=rt60_sabine_bands_500)
# measure_rt60(one_pole_tonal_correction_rir, fs=fs, plot=True, rt60_tgt=rt60_sabine_bands_500)

# plt.figure(figsize=(10, 4))
# plt.title('ISM-FDN (FIR) RT60')
# measure_rt60(fir_rir, fs=fs, plot=True, rt60_tgt=rt60_sabine_bands_500)

plt.show()
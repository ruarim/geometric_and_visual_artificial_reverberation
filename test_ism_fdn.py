import numpy as np
from matplotlib import pyplot as plt
from pyroomacoustics.experimental.rt60 import measure_rt60

from utils.matlab import init_matlab_eng
from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from early_reflections.ism import ImageSourceMethod
from early_reflections.early_reflections import EarlyReflections
from utils.point3D import Point3D
from utils.signals import signal
from utils.plot import plot_comparision, plot_spectrogram, plot_signal
from utils.reverb_time import ReverbTime
from utils.file import write_array_to_wav
from utils.absorption import Absorption
from utils.filters import tone_correction
from utils.room import calc_mean_free_path
from utils.geometry import distance_to_delay
from utils.primes import find_log_mutual_primes, find_closest_primes

# config dataclasses
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

print(room_config.ROOM_DIMS)

# get the absoprtion coefficients at frequnecy bands for each wall
absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, simulation_config.FS)

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config, fs=simulation_config.FS) # pass specific config values instead
ism_er_rir = ism.render(norm=True) # rendering early reflections with pyroomacoustics ism
image_source_coords, image_source_walls = ism.get_source_coords(show=False)
image_source_points = [Point3D(image_source) for image_source in image_source_coords]
source_point = Point3D(room_config.SOURCE_LOC)
mic_point = Point3D(room_config.MIC_LOC)


absorption_coeffs = absorption.coefficients
absorption_bands = absorption.freq_bands
absorption.plots_coefficients()

# tapped delay line or render ism and convolve with input
er = EarlyReflections(
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

# inject room details from room object
reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s_bands(absorption_coeffs, absorption_bands, plot=True)
rt60_sabine_bands_500 = rt60_sabine[2]
rt60_eyring_bands_500 = rt60_eyring[2]
tranistion_frequency = reverb_time.transition_frequency(rt60_sabine_bands_500, multiple=4)

# use table instead
print(f'Center Frequnecies:       {absorption_bands}')
print(f'RT60 Bands Sabine:        {rt60_sabine}')
print(f'RT60 Bands Eyring:        {rt60_eyring}')
print(f'RT60 Bands Sabine 500 Hz: {rt60_sabine_bands_500}')
print(f'RT60 Bands Eyring 500 Hz: {rt60_eyring_bands_500}')
print(f'Transition Frequnecy:     {tranistion_frequency}')

mean_free_path = calc_mean_free_path(reverb_time.V, np.sum(reverb_time.S))
mean_free_path_delay = int(distance_to_delay(mean_free_path, simulation_config.SPEED_OF_SOUND) * (simulation_config.FS))

print(f'Mean Free Path Delay: {mean_free_path_delay}')

# delay from log mutual primes around mean free path
# fdn_order = 8
# log_mutal_primes = find_log_mutual_primes(mean_free_path_delay, fdn_order, percentage=75)
# fdn_delay_times = np.array(log_mutal_primes)

# from colourless FDN paper
# fdn_delay_times = np.array([809, 877, 937, 1049, 1151, 1249, 1373, 1499])

# delay from geometry
fdn_delay_times = np.array([int(delay_sec * simulation_config.FS) for delay_sec in set(er.delay_times)])
fdn_delay_times = find_closest_primes(fdn_delay_times)
print(f'FDN Delays {fdn_delay_times}')

# run acoustic simulation
input_signal, fs = signal(
        test_config.SIGNAL_TYPE, 
        simulation_config.SIGNAL_LENGTH, 
        simulation_config.FS, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
)

ism_fdn_output_signal = np.zeros_like(input_signal)

print('TDL: processing early reflections')
er_signal_tdl,      direct_sound = er.process(input_signal, ism_fdn_output_signal, type='tdl')
er_signal_convolve, direct_sound = er.process(input_signal, ism_fdn_output_signal, type='convolve')

# start matlab process
matlab_eng = init_matlab_eng()

print('FDN: processing late reverberation')
# apply FDN reverberation to output of early reflection stage
lr_signal_one_pole = np.array(matlab_eng.velvet_fdn_one_pole(simulation_config.FS, er_signal_tdl, fdn_delay_times, rt60_sabine, absorption_bands, tranistion_frequency))
lr_signal_fir      = np.array(matlab_eng.velvet_fdn_fir(simulation_config.FS, er_signal_tdl, fdn_delay_times, rt60_sabine, absorption_bands))

# end matlab process
matlab_eng.quit()

# mono
lr_signal_one_pole = np.array([x[0] for x in lr_signal_one_pole])
lr_signal_fir      = np.array([x[0] for x in lr_signal_fir])

# tonal correction filter (gains = average of room absorption coefficients)
filter_taps = 200
lr_signal_one_pole_tonal_correction = tone_correction(
        lr_signal_one_pole, 
        absorption_coeffs, 
        absorption_bands, 
        simulation_config.FS, 
        taps=filter_taps, 
        plot=True)

# combine early and late reflections to create full RIRs
ism_fdn_one_pole_rir = er_signal_tdl + lr_signal_one_pole + direct_sound
ism_fdn_one_pole_tonal_correction_rir = er_signal_tdl + lr_signal_one_pole_tonal_correction + direct_sound
ism_fdn_fir_rir = er_signal_tdl + lr_signal_fir + direct_sound

config_str = f'ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}_One-Pole", ism_fdn_one_pole_rir, simulation_config.FS)
write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}_One-Pole_Tonal_Correction", ism_fdn_one_pole_tonal_correction_rir, simulation_config.FS)    
write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}_FIR", ism_fdn_fir_rir, simulation_config.FS)    

# render full rir for comparison
ism_order = 100
ism_rir = ism.render(order=ism_order)

# plot
compare_data = {
        "Full IMS": ism_rir / np.max(ism_rir),
        "Direct Sound": direct_sound,
        "Early ISM": ism_er_rir / np.max(ism_er_rir),
        "Early TDL": er_signal_tdl,
        "FDN One-Pole": lr_signal_one_pole,
        "FDN One-Pole Tonal Correction": lr_signal_one_pole_tonal_correction,
        'FDN FIR': lr_signal_fir,
}

xlim = [0, 1]

# time plots comparison
plot_comparision(
        compare_data, 
        'ISM-FDN Comparison', 
        xlim=xlim, 
        plot_time=True,
        y_offset=0.0
)

# spectrograms
plot_spectrogram(ism_rir, simulation_config.FS, xlim=xlim, title="Spectrogram of ISM RIR")
plot_spectrogram(ism_fdn_one_pole_rir, simulation_config.FS, xlim=xlim, title="Spectrogram of ISM-FDN (one-pole absorption) RIR")
plot_spectrogram(ism_fdn_one_pole_tonal_correction_rir, simulation_config.FS, xlim=xlim, title="Spectrogram of ISM-FDN (one-pole absorption and Tonal Correction) RIR")
plot_spectrogram(ism_fdn_fir_rir, simulation_config.FS, xlim=xlim, title="Spectrogram of ISM-FDN (FIR absorption) RIR")

comparison = {
        'one-pole fdn': lr_signal_one_pole,
        'one-pole tonal correction fdn': lr_signal_one_pole_tonal_correction,
        'fir fdn' : lr_signal_fir,
}
plot_comparision(comparison, xlim=xlim, plot_time=True)

# RT60s
plt.figure(figsize=(10, 4))
plt.title('ISM RT60')
measure_rt60(ism_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_sabine_bands_500)

plt.figure(figsize=(10, 4))
plt.title('ISM-FDN (one-pole) RT60')
measure_rt60(ism_fdn_one_pole_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_sabine_bands_500)
measure_rt60(ism_fdn_one_pole_tonal_correction_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_sabine_bands_500)

plt.figure(figsize=(10, 4))
plt.title('ISM-FDN (FIR) RT60')
measure_rt60(ism_fdn_fir_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_sabine_bands_500)

plt.show()
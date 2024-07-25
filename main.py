import numpy as np
from matplotlib import pyplot as plt
from pyroomacoustics.experimental.rt60 import measure_rt60
from math import floor

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
from sdn.simulation import run_sdn_simulation

        
# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

# get the absoprtion coefficients at frequnecy bands for each wall
absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, simulation_config.FS)
print(absorption.extrapolated_freq_bands)
print(absorption.extrapolated_coeffs)

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config, fs=simulation_config.FS) # pass specific config values instead
ism_er_rir = ism.render(norm=True) # rendering early reflections with pyroomacoustics ism
image_source_coords, image_source_walls = ism.get_source_coords(show=False)
image_source_points = [Point3D(image_source) for image_source in image_source_coords]
source_point = Point3D(room_config.SOURCE_LOC)
mic_point = Point3D(room_config.MIC_LOC)

# tapped delay line or render ism and convolve with input
er = EarlyReflections(
        source_point,  
        mic_point, 
        image_source_points,
        image_source_walls,
        simulation_config,
        room_config,
        ism_rir=ism_er_rir,
)

reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s()
rt60_sabine_bands, rt60_eyring_bands = reverb_time.rt60s_bands(absorption.extrapolated_coeffs, absorption.extrapolated_freq_bands, plot=True)

print(rt60_sabine, rt60_eyring)
print(rt60_sabine_bands, rt60_eyring_bands)

# from mean free path
fdn_delay_times = np.array([809, 877, 937, 1049, 1151, 1249, 1373, 1499]) # log distributed prime numbers, TODO: mutual prime around mean free path

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
er_signal_tdl = er.process(input_signal, ism_fdn_output_signal, type='tdl')
er_signal_convolve = er.process(input_signal, ism_fdn_output_signal, type='convolve')

# start matlab process
matlab_eng = init_matlab_eng()

print('FDN: processing late reverberation')
# apply FDN reverberation to output of early reflection stage
lr_signal = np.array(matlab_eng.velvet_fdn(simulation_config.FS, er_signal_tdl, fdn_delay_times, rt60_eyring_bands, absorption.extrapolated_freq_bands))

# apply in parralel
# input should be delayed by shortest image source
# lr_signal = np.array(matlab_eng.velvet_fdn(simulation_config.FS, input_signal, fdn_delay_times, rt60_sabine))

# end matlab process
matlab_eng.quit()

# mono 
ism_fdn_rir = np.array([er + lr[0] for er, lr in zip(er_signal_tdl, lr_signal)])

# simulate room with SDN
print("SDN: processing samples...")
sdn_rir = run_sdn_simulation(
        input_signal,  
        room_config.ROOM_DIMS, 
        room_config.SOURCE_LOC, 
        room_config.MIC_LOC, 
        fs=simulation_config.FS,
        flat_absorption=0.1,
        er_order=1,
        direct_path=True
)

# render pyroomacoustics rir for comparison
ism_order = 100
ism_rir = ism.render(order=ism_order)
ism_full_rir_norm = ism_rir / np.max(ism_rir)

config_str = f'ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

if output_config.OUTPUT_TO_FILE:
        # output early reflections RIR
        write_array_to_wav(test_config.ER_RIR_DIR, test_config.SIGNAL_TYPE, er_signal_tdl, simulation_config.FS)
        write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}", ism_fdn_rir, simulation_config.FS)

if output_config.PLOT:
        absorption.plots_coefficients()
        
        # plot
        compare_data = {
                # "Convolution": er_signal_convolve,
                "Velvet FDN": lr_signal,
                'Tapped Delay Line': er_signal_tdl,
                "Full ISM": ism_full_rir_norm,
        }

        xlim = [0, 500]
        offset_ref = ism_fdn_rir
        y_offset = np.max(offset_ref) + np.abs(np.min(offset_ref))

        plot_comparision(
                compare_data, 
                f'ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}', 
                xlim=xlim, 
                plot_time=True,
                y_offset=0.0
        )
        
        # plot_signal(sdn_rir, plot_time=True)
        
        spec_xlim=[0,6]
        plot_spectrogram(ism_fdn_rir, simulation_config.FS, xlim=spec_xlim, title="Spectrogram of ISM/Velvet FDN RIR")
        plot_spectrogram(ism_rir, simulation_config.FS, xlim=spec_xlim, title="Spectrogram of ISM RIR")
        plot_spectrogram(sdn_rir, simulation_config.FS, xlim=spec_xlim, title="Spectrogram of SDN RIR")
        
        plt.figure(figsize=(10, 4))
        plt.title(f'ISM RT60, Order: {ism_order}')
        measure_rt60(ism_fdn_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_eyring_bands[floor(len(rt60_eyring_bands) / 2)])
        
        plt.figure(figsize=(10, 4))
        plt.title('ISM/FDN RT60')
        measure_rt60(ism_fdn_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_eyring_bands[floor(len(rt60_eyring_bands) / 2)])

        plt.figure(figsize=(10, 4))
        plt.title('SDN RT60')
        measure_rt60(sdn_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_eyring)

        plt.show()
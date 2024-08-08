import numpy as np
from matplotlib import pyplot as plt
from librosa import power_to_db
from pyroomacoustics.experimental.rt60 import measure_rt60

from utils.signals import signal
from utils.plot import plot_comparison, plot_signal, plot_spectrogram
from config import SimulationConfig, RoomConfig, TestConfig

# configs
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()


# # ISM RIR
# ism_rir = signal()

# # Ray Tracing RIR
# rt_rir = signal()

# # ISM/Ray Tracing RIR
# ism_rt_rir = signal()

# # SDN rir 
# sdn_rir = signal()

# # ISM/Standard FDN RIR
# ism_hadamard_fdn_rir = signal()

# # ISM/Velvet FDN RIR
# ism_velvet_fdn_rir = signal()

# Real RIR
real_rir, real_rir_fs = signal(
                "file", 
                44100,
                data_dir='_data/CR2 small room (seminar room)/RIRs/wav/', 
                file_name="CR2_RIR_LS1_MP2_Dodecahedron.wav",
                channels=1
)
        
plot_signal(real_rir, fs=real_rir_fs)
plot_spectrogram(real_rir, real_rir_fs)
plt.figure(figsize=(10, 4))
real_rt60 = measure_rt60(real_rir, fs=simulation_config.FS, plot=True)

# plot_signal(ism_full_rir, title="Image Source Method RIR", xlim=xlim)
# plot_signal(output_signal, 'Early Reflections - Tapped Delay Line', xlim=xlim)
# plot_signal(lr_signal, "Late Reflections - FDN")
# plot_signal(full_ir, "Full IR")
                        
# plot_signal(full_rir, fs=simulation_config.FS, xlim=xlim, plot_time=True)
# spec_xlim = [0, 10]
# spec_y_scale = 'linear'
# plot_spectrogram(full_rir, sr=simulation_config.FS, title='Spectrogram of ISM/FDN RIR', xlim=spec_xlim, y_scale=spec_y_scale)
# plot_spectrogram(ism_full_rir_norm, sr=simulation_config.FS, title='Spectrogram of ISM RIR', xlim=spec_xlim, y_scale=spec_y_scale)
                
# plt.figure(figsize=(10, 4))
# full_rir_rt60 = measure_rt60(full_rir, fs=simulation_config.FS, plot=True)
# time_vec = np.arange(len(full_rir)) / (simulation_config.FS)
# full_rir_power = full_rir**2
# plt.plot(time_vec, power_to_db(full_rir_power, ref=np.max(full_rir_power)))
# print(full_rir_rt60)
                
# plt.figure(figsize=(10, 4))
# ism_rir_rt60 = measure_rt60(ism_rir, fs=simulation_config.FS, plot=True)
# time_vec = np.arange(len(ism_rir)) / (simulation_config.FS)
# ism_rir_power = ism_rir**2
# plt.plot(time_vec, power_to_db(ism_rir_power, ref=np.max(ism_rir_power)))
# print(ism_rir_rt60)
        
plt.show()
import numpy as np
from matplotlib import pyplot as plt
from pyroomacoustics.experimental.rt60 import measure_rt60

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.signals import signal
from utils.plot import plot_spectrogram, plot_signal
from utils.reverb_time import ReverbTime
from utils.absorption import Absorption
from sdn.simulation import run_sdn_simulation
from utils.file import write_array_to_wav
from early_reflections.ism import ImageSourceMethod

# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

# get the absoprtion coefficients at frequnecy bands for each wall
absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, simulation_config.FS)
absorption_coeffs = absorption.coefficients + absorption.air_absorption
absorption_bands = absorption.freq_bands

reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s_bands(absorption_coeffs, absorption_bands, plot=True)

print(f"RT60 Sabine: {rt60_sabine}")
print(f"RT60 Eyring: {rt60_eyring}")

# run acoustic simulation
input_signal, fs = signal(
        test_config.SIGNAL_TYPE, 
        simulation_config.SIGNAL_LENGTH, 
        simulation_config.FS, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
)

# simulate room with SDN
print("SDN: processing samples...")
sdn_rir = run_sdn_simulation(
        input_signal,  
        room_config.ROOM_DIMS, 
        room_config.SOURCE_LOC, 
        room_config.MIC_LOC,
        er_order=1,
        fs=simulation_config.FS,
        absorption_coefficients=absorption_coeffs,
        absorption_freqs=absorption_bands,
        flat_absorption=1,
        direct_path=True
)

# apply tonal correction?

print('ISM: simulating room')
ism = ImageSourceMethod(room_config, fs=simulation_config.FS)

# render full rir for comparison
ism_order = 100
ism_rir = ism.render(order=ism_order, plot_rt60=True)
ism_full_rir_norm = ism_rir / np.max(ism_rir)

config_str = f'SDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'
write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}", sdn_rir, simulation_config.FS)

plt.figure(figsize=(10, 4))
plt.title('SDN RT60')
sdn_rt60 = measure_rt60(sdn_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_sabine[2])

plt.figure(figsize=(10, 4))
plt.title('ISM RT60')
ism_rt60 = measure_rt60(ism_rir, fs=simulation_config.FS, plot=True, rt60_tgt=rt60_sabine[2])

xlim=[0, sdn_rt60]
plot_signal(sdn_rir, plot_time=True, title=f"{config_str}")
plot_spectrogram(sdn_rir, simulation_config.FS, xlim=None, title="Spectrogram of SDN RIR")
plot_spectrogram(ism_rir, simulation_config.FS, xlim=None, title="Spectrogram of ISM RIR")

plt.show()
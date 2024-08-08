from matplotlib import pyplot as plt
import numpy as np

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.plot import plot_spectrogram, plot_comparison, plot_signal
from utils.signals import signal
from utils.file import write_array_to_wav
from ism_fdn import ISMFDN
from utils.convolve import fft_convolution

# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

sample, fs = signal(
        'file', 
        simulation_config.SIGNAL_LENGTH,
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
)

unit_impulse, _ = signal(
        'unit', 
        simulation_config.SIGNAL_LENGTH, 
        fs,
)

one_pole_rir, fir_rir = ISMFDN(
        fs, 
        simulation_config, 
        room_config, 
        fdn_N=-1, 
        crossover_freq_multiple=room_config.SCHRODER_MULTIIPLE,
        processing_type='parallel',
).process(unit_impulse)

config_str = f'Parallel ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

one_pole_processed_sample = fft_convolution(sample, one_pole_rir)
fir_processed_sample = fft_convolution(sample, fir_rir)

# output
write_array_to_wav(
        test_config.FULL_RIR_DIR, 
        f"{config_str} One Pole", 
        one_pole_rir, fs
)
write_array_to_wav(
        test_config.FULL_RIR_DIR, 
        f"{config_str} FIR", 
        fir_rir, 
        fs
)
write_array_to_wav(
        test_config.PROCESSED_SAMPLES_DIR,
        f"{config_str} {test_config.FILE_NAME} One Pole",
        one_pole_processed_sample / np.max(one_pole_processed_sample),
        fs
)
write_array_to_wav(
        test_config.PROCESSED_SAMPLES_DIR, 
        f"{config_str} {test_config.FILE_NAME} FIR", 
        fir_processed_sample / np.max(fir_processed_sample), 
        fs
)

# plot
spec_xlim = [0, 2]
wave_xlim = [0, 0.5]
compare = {
        'RIR One Pole': one_pole_rir,
        'RIR FIR': fir_rir,
}

plot_spectrogram(one_pole_rir, fs, xlim=spec_xlim, title='rir_one_pole')
plot_spectrogram(fir_rir, fs, xlim=spec_xlim, title='rir_fir')
plot_comparison(compare, xlim=wave_xlim)
plot_signal(fir_rir,  xlim=wave_xlim, title='rir_fir')
plot_signal(one_pole_rir,  xlim=wave_xlim, title='rir_one_pole')
plt.show()
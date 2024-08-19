from matplotlib import pyplot as plt
import numpy as np

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.plot import plot_spectrogram, plot_comparison, plot_signal
from utils.signals import signal
from ism_fdn import ISMFDN
from utils.room import Room

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
        plot=True,
).process(unit_impulse)

config_str = f'Parallel ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

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
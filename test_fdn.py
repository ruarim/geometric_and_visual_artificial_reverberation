import numpy as np
from matplotlib import pyplot as plt

from utils.matlab import init_matlab_eng
from utils.plot import plot_spectrogram, plot_signal
from utils.signals import signal
from utils.reverb_time import ReverbTime
from utils.absorption import Absorption
from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig

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

# log distributed mutual primes from colourless FDN paper (TODO: ref)
fdn_delay_times = np.array([809, 877, 937, 1049, 1151, 1249, 1373, 1499])

x, _ = signal('unit', fs * 3, fs)

# start matlab process
matlab_eng = init_matlab_eng()

rir =  matlab_eng.standard_fdn(fs, x, fdn_delay_times, rt60_sabine)

rir = np.array([t[0] for t in rir])

# end matlab process
matlab_eng.quit()

plot_signal(rir, plot_time=True)
plot_spectrogram(rir, fs)
plt.show()
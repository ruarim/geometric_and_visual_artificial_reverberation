import numpy as np
from matplotlib import pyplot as plt

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.signals import signal
from utils.reverb_time import ReverbTime
from utils.absorption import Absorption
from utils.filters import plot_fir

        
# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

# get the absoprtion coefficients at frequnecy bands for each wall
absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, simulation_config.FS)
absorption.plots_coefficients()

reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s()
rt60_sabine_bands, rt60_eyring_bands = reverb_time.rt60s_bands(absorption.extrapolated_coefficients, absorption.extrapolated_freq_bands, plot=True)

# frequency bands and attenuation values
freqs = absorption.extrapolated_freq_bands
coefficients = absorption.extrapolated_coefficients[0]

# get alpha from absorption coeffs
alphas = 1 - coefficients

x, fs = signal('noise', burst_secs=0.5)

plot_fir(x, freqs, alphas, fs, db=True, y_scale='log')

plt.show()
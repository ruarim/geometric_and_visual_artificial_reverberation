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
rt60_sabine, rt60_eyring = reverb_time.theory_rt60s()
rt60_sabine_bands, rt60_eyring_bands = reverb_time.theory_rt60s_bands(absorption.coefficients, absorption.freq_bands, plot=True)

# frequency bands and attenuation values
freqs = absorption.freq_bands
wall_coefficients = absorption.coefficients[0]  # test with one wall
wall_air_coefficients = absorption.coefficients[0] + absorption.air_absorption # test with one wall and air
 

# test noise burst
x, fs = signal('noise', burst_secs=0.5)

# get alpha from absorption coeffs
wall_alphas = 1 - wall_coefficients
plot_fir(x, freqs, wall_alphas, fs, db=True, title='Wall Absorption')

wall_air_alphas = 1 - wall_air_coefficients
plot_fir(x, freqs, wall_air_alphas, fs, db=True, title='Wall and Air Absorption')
plt.ylim([-5, 0])
plt.xlim([50, int(fs/2)])

plt.show()
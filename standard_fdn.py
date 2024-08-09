import numpy as np
from math import sqrt

from utils.matlab import init_matlab_eng
from utils.reverb_time import ReverbTime
from utils.absorption import Absorption
from config import RoomConfig

class StandardFDN:
    def __init__(self, fs: float, room_config: RoomConfig):
        self.fs = fs

        # get the absoprtion coefficients at frequnecy bands for each wall
        absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, self.fs)
        absorption_coeffs = absorption.coefficients + absorption.air_absorption
        absorption_bands = absorption.freq_bands

        reverb_time = ReverbTime(room_config)
        self.rt60_sabine, _ = reverb_time.rt60s_bands(absorption_coeffs, absorption_bands)

        # log distributed mutual primes from paper (Feedback Delay Network Optimization G. D. Santo et al. 2024)
        self.fdn_delay_times = np.array([809, 877, 937, 1049, 1151, 1249, 1373, 1499])

        self.scaling_factor = 1 / sqrt(len(self.fdn_delay_times))

    def process(self, x):
        print('Standard FDN Processing...')
        # start matlab process
        matlab_eng = init_matlab_eng()

        y =  matlab_eng.standard_fdn(self.fs, x * self.scaling_factor, self.fdn_delay_times, self.rt60_sabine)
        y = np.array([t[0] for t in y])

        # end matlab process
        matlab_eng.quit()
                
        return y
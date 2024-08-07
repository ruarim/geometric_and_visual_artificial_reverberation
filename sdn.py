import numpy as np
from matplotlib import pyplot as plt

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.plot import plot_spectrogram
from utils.absorption import Absorption
from scattering_delay_network.simulation import run_sdn_simulation

# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

class SDN:
        def __init__(self, fs: float, simulation_config: SimulationConfig, room_config: RoomConfig):
                # get the absoprtion coefficients at frequnecy bands for each wall
                self.fs = fs
                absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, simulation_config.FS)
                self.absorption_coeffs = absorption.coefficients + absorption.air_absorption
                self.absorption_bands = absorption.freq_bands

        def process(self, x):
                print(f'SDN Processing...')
                y = run_sdn_simulation(
                        x,  
                        room_config.ROOM_DIMS, 
                        room_config.SOURCE_LOC, 
                        room_config.MIC_LOC,
                        er_order=1,
                        fs=self.fs,
                        absorption_coefficients=self.absorption_coeffs,
                        absorption_freqs=self.absorption_bands,
                        flat_absorption=1,
                        direct_path=True
                )                
                return y
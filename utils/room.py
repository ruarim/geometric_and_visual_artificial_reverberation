# class to hold all room details / calculation
# dimension
# materials for walls
# humidity
# temp
# etc
import numpy as np
from config import RoomConfig
from utils.absorption import Absorption
from utils.reverb_time import ReverbTime
from utils.plot import plot_room

# TODO: intergrate into room simulation algorithms
class Room:
    def __init__(self, fs, room_config: RoomConfig, plot=False):
        self.fs = fs
        self.room_dims = room_config.ROOM_DIMS
        self.source = room_config.SOURCE_LOC
        self.mic = room_config.MIC_LOC
        self.wall_materials = room_config.WALL_MATERIALS
        self.wall_materials_type = room_config.WALL_MATERIALS_TYPE
        
        # get the absoprtion coefficients at frequnecy bands for each wall
        absorption = Absorption(room_config.WALL_MATERIALS, room_config.MATERIALS_DIR, self.fs)

        reverb_time = ReverbTime(room_config)
        self.rt60_sabine_bands, self.rt60_eyring_bands = reverb_time.rt60s_bands(absorption.coefficients, absorption.freq_bands, plot=plot)

        # frequency bands and attenuation values
        self.center_freqs = absorption.freq_bands
        self.wall_air_coefficients = absorption.coefficients + absorption.air_absorption # test with one wall and air
        
        self.V = reverb_time.V
        self.S = reverb_time.S
        
        if plot:
            absorption.plots_coefficients()
            plot_room(self.room_dims, self.source, self.mic)
    
    def valid_shape(self):
        assert all(dim > 0 for dim in self.room_dims), "invalid room shape"
    
    def valid_source_mic(self):
        # Ensure source and mic positions are within room dimensions
        assert np.all(np.array(self.source) < np.array(self.room_dims)), "Source position must be within room dimensions."
        assert np.all(np.array(self.mic) < np.array(self.room_dims)), "Mic position must be within room dimensions."
        
        # Ensure source and mic positions are greater than (0, 0, 0)
        assert np.all(np.array(self.source) > np.array([0, 0, 0])), "Source position must be greater than (0, 0, 0)."
        assert np.all(np.array(self.mic) > np.array([0, 0, 0])), "Mic position must be greater than (0, 0, 0)."
    
    def calc_mean_free_path(self):
        """
        V: Room volume
        S: Total surface area
        """
        return (4 * self.V) / self.S
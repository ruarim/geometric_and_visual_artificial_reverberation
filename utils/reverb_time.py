# an evaluation of 
# - t60 againt sabine and eyring formulas
# - echo density
# - mode density
# - energy decay relief (energy decay at frequecy bands)
# - frequency-dependent reverberation time
# - early decay time

# direct path component should be removed for evaluation

import numpy as np
from matplotlib import pyplot as plt
from config import RoomConfig

class ReverbTime:
    def __init__(self, room_config: RoomConfig):
        self.room_dims = room_config.ROOM_DIMS
        self.absorption_flat = np.array([room_config.WALL_ABSORPTION[wall] for wall in room_config.WALL_ABSORPTION])
        self.V = self.calc_V(self.room_dims)
        self.A = self.calc_A(self.room_dims)
    
    @staticmethod
    def calc_V(dims):
        """
        Calculate the Volume of a room.
        
        Parameters:
        walls (array): Array of wall dimensions - [ length, width, height ]
            
        Returns:
        V (float): Volume of the room in cubic meters.
        """
        if len(dims) != 3 or any(dim <= 0 for dim in dims):
            raise ValueError("Invalid room dimensions provided.")
        
        return dims[0] * dims[1] * dims[2]

    @staticmethod
    def calc_A(dims):
        """
        Calculate the surface area of walls in a room.
        
        Parameters:
        dims (array): Array of wall dimensions - [ length, width, height ]
            
        Returns:
        A (numpy array): Array of surface areas of materials in square meters.
        """
        if len(dims) != 3 or any(dim <= 0 for dim in dims):
            raise ValueError("Invalid wall dimensions provided.")
        
        front_back = dims[0] * dims[2]
        side = dims[1] * dims[2]
        
        return np.array([front_back, front_back, side, side, side, side])

    @staticmethod
    def sabine_rt60(V: float, A, alpha):
        """
        Calculate reverberation time using Sabine's formula.
        
        Parameters:
        V (float): Volume of the room in cubic meters.
        A (numpy array): Array of surface areas of materials in square meters.
        alpha (numpy array): Array of absorption coefficients of materials.
        
        Returns:
        float: Reverberation time in seconds.
        """
        scaling_factor = 0.161
        if np.any(alpha < 0) or np.any(alpha > 1):
            raise ValueError("Absorption coefficients should be between 0 and 1.")
        return (scaling_factor * V) / np.sum(A * alpha)

    @staticmethod
    def eyring_rt60(V: float, A, alpha):
        """
        Calculate reverberation time using Eyring's formula.
        
        Parameters:
        V (float): Volume of the room in cubic meters.
        A (numpy array): Array of surface areas of materials in square meters.
        alpha (numpy array): Array of absorption coefficients of materials (dimensionless).
        
        Returns:
        float: Reverberation time in seconds.
        """
        scaling_factor = 0.161
        if np.any(alpha < 0) or np.any(alpha > 1):
            raise ValueError("Absorption coefficients should be between 0 and 1.")
        
        total_absorption = np.sum(A * alpha)
        total_area = np.sum(A)
        
        if total_absorption >= total_area:
            raise ValueError("Total absorption cannot be greater than or equal to total area.")
        
        return (scaling_factor * V) / (-total_area * np.log(1 - total_absorption / total_area)) # is "-total_area" correct

    def rt60s(self):        
        sabine = self.sabine_rt60(self.V, self.A, self.absorption_flat)
        eyring = self.eyring_rt60(self.V, self.A, self.absorption_flat)

        return sabine, eyring
    
    def rt60s_bands(self, alphas: list[list], bands: list[float], plot=False):
        sabine_bands = np.array([self.sabine_rt60(self.V, self.A, alphas[:, i]) for i in range(len(alphas[0]))])
        eyring_bands = np.array([self.eyring_rt60(self.V, self.A, alphas[:, i]) for i in range(len(alphas[0]))])
        
        rt60s = {
            "Sabine": sabine_bands,
            "Eyring": eyring_bands 
        }
        
        if plot:
            self._plot_rt60_bands(rt60s, bands)
        
        return sabine_bands, eyring_bands
    
    def _plot_rt60_bands(self, rt60s, bands):
        """
        Plot the coefficents at frequnecy bands for each wall
        """
        plt.figure(figsize=(10, 4))
        plt.xscale('log')
        plt.xticks(bands, labels=[str(band) for band in bands])

        plt.xlabel('Bands')
        plt.ylabel('Reverb Time (-60dB secs)')
        plt.title('Predicted Reverb Time at Frequency Bands')
        
        for rt60_type in rt60s:
            plt.plot(bands, rt60s[rt60_type], label=rt60_type)
        
        plt.legend()
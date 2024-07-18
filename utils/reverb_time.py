# an evaluation of 
# - t60 againt sabine and eyring formulas
# - echo density
# - mode density
# - energy decay relief (energy decay at frequecy bands)
# - frequency-dependent reverberation time
# - early decay time

# direct path component should be removed for evaluation

import numpy as np
from config import RoomConfig

# from evaluation.rt60 import measure_rt60


# def calc_T60(h, fs, compare, plot=False):
#     """
#     Calculate the T60 reverberation time of the SDN simulation in seconds.
    
#     Parameters:
#     walls (array): Array of wall dimensions - [ length, width, height ]
        
#     Returns:
#     T60 (float): Reverberation time in seconds.
#     """
#     t60 = measure_rt60(h, fs, plot=plot)
#     return t60

class ReverbTime:
    def __init__(self, room_config: RoomConfig):
        self.room_dims = room_config.ROOM_DIMS
        self.absorption = np.array([room_config.WALL_ABSORPTION[wall] for wall in room_config.WALL_ABSORPTION])
    
    def calc_V(self, dims):
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

    def calc_A(self, dims):
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

    def sabine_rt60(self, V: float, A, alpha):
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

    def eyring_rt60(self, V: float, A, alpha):
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
        V = self.calc_V(self.room_dims)
        A = self.calc_A(self.room_dims)

        sabine = self.sabine_rt60(V, A, self.absorption)
        eyring = self.eyring_rt60(V, A, self.absorption)

        return sabine, eyring
    
    def rt60_bands(self):
        pass
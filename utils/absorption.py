from matplotlib import pyplot as plt
import numpy as np
from math import floor

from utils.file import read_json

class Absorption:
    air_absorption_table = {
        "10C_30-50%": [x * 1e-3 for x in [0.1, 0.2, 0.5, 1.1, 2.7, 9.4, 29.0]],
        "10C_50-70%": [x * 1e-3 for x in [0.1, 0.2, 0.5, 0.8, 1.8, 5.9, 21.1]],
        "10C_70-90%": [x * 1e-3 for x in [0.1, 0.2, 0.5, 0.7, 1.4, 4.4, 15.8]],
        "20C_30-50%": [x * 1e-3 for x in [0.1, 0.3, 0.6, 1.0, 1.9, 5.8, 20.3]],
        "20C_50-70%": [x * 1e-3 for x in [0.1, 0.3, 0.6, 1.0, 1.7, 4.1, 13.5]],
        "20C_70-90%": [x * 1e-3 for x in [0.1, 0.3, 0.6, 1.1, 1.7, 3.5, 10.6]],
        "center_freqs": [125, 250, 500, 1000, 2000, 4000, 8000],
    }
    
    def __init__(self, walls_material: dict, data_dir: str, fs: float, air_absorption='20C_30-50%'):
        self.air_absorption = air_absorption
        self.fs = fs
        self.materials: dict = read_json(data_dir)
        self.walls_material = walls_material
        self.freq_bands = np.array(self.materials["center_freqs"])
        self.coefficients = self._get_coefficients()
        self.coefficients_dict = self._get_coefficients_dict()
        # TODO: add seperate air absorption variable
        
    def plots_coefficients(self):
        """
        Plot the coefficents at frequnecy bands for each wall
        """
        plt.figure(figsize=(10, 4))
        plt.xscale('log')
        plt.xticks(self.freq_bands, labels=[str(band) for band in self.freq_bands])

        plt.xlabel('Bands')
        plt.ylabel('Absorption Coefficient')
        plt.title('Plot of Material Absorption Coefficients vs. Bands')
        
        for coefficients, wall in zip(self.coefficients, self.walls_material):
            plt.plot(self.freq_bands, coefficients, label=f"{wall} - {self.walls_material[wall]}")
        
        plt.legend()
        
    def _extrapolate_coefficients(self):
        """
        Extrapolate maximum and minimum absorption values
        """
        # add the frequency bands
        # dc = 0
        # nyquist = self.fs / 2
        max_band = self.freq_bands[-1]
        min_band = self.freq_bands[0]
        self.extrapolated_freq_bands = np.concatenate(([floor(min_band / 2)], self.freq_bands, [max_band * 2]))
        
        # for each wall extrapolate coeffs to 0 Hz and Nyquist            
        return np.array([self._extrapolate_coeffs(i) for i in range(len(self.coefficients))])
       
    def _extrapolate_coeffs(self, i):
        wall_coeffs = self.coefficients[i]
        max_band = wall_coeffs[-1]
        min_band = wall_coeffs[0]
        
        return np.concatenate(([min_band], wall_coeffs, [max_band]))
            
    def _get_coefficients(self):
        """
        Given a list of material names get the corresponding values from the materials data.
        
        Returns:
        list: A 2D list of coefficients associated with each material name
        """
        coeffs_property = "coeffs"
        return np.array([np.array(self._find_value_by_key(self.materials, material, coeffs_property) + self._get_air_absorption(self.air_absorption)) for _, material in self.walls_material.items()])
    
    def _get_coefficients_dict(self):
        """
        Given a list of material names get the corresponding values from the materials data.
        
        Returns:
        dict: A dict with (key) wall name and (value) coefficients associated with each material name
        """
        coeffs_property = "coeffs"
        coeffs_dict = {}
        for wall_name, material in self.walls_material.items():
            coeffs_dict[wall_name] = np.array(self._find_value_by_key(self.materials, material, coeffs_property)) + self._get_air_absorption(self.air_absorption)
                
        return coeffs_dict

    def _get_air_absorption(self, temp_humidity: str):
        return np.array(self.air_absorption_table[temp_humidity])   
            
    @staticmethod
    def _find_value_by_key(d, target_key, property):
        """
        Recursively search for values by key in a nested dictionary.

        Parameters:
        d (dict): The dictionary to search.
        target_key (str): The key to search for.

        Returns:
        list: A list of values associated with the target key.
        """
        found_value = None

        def search(d):
            nonlocal found_value
            if isinstance(d, dict):
                for key, value in d.items():
                    if key == target_key:
                        found_value = value[property]
                    if isinstance(value, dict):
                        search(value)
                    if found_value is not None:
                        return

        search(d)
        return found_value
    
    
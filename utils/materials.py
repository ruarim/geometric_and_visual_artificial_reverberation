from matplotlib import pyplot as plt
import numpy as np

from utils.file import read_json

class Materials:
    def __init__(self, walls_material: dict, data_dir: str, fs: float):
        self.fs = fs
        self.materials: dict = read_json(data_dir)
        self.walls_material = walls_material
        self.freq_bands = np.array(self.materials["center_freqs"])
        self.materials_coeffs = self._get_coefficients()
        self.extrapolated_coeffs = self._extrapolate_dc_nyquist()
    
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
        
        for coefficients, wall in zip(self.materials_coeffs, self.walls_material):
            plt.plot(self.freq_bands, coefficients, label=f"{wall} - {self.walls_material[wall]}")
        
        plt.legend()
        
    def _extrapolate_dc_nyquist(self):
        """
        For now this is a relativly crude approximation.
        
        Add coefficients down to 0 Hz and up to Nyquist using same value as the lowest/largest frequency coefficents.
        """
        # add the frequency bands
        dc = 0
        nyquist = self.fs / 2
        self.extrapolated_freq_bands = np.concatenate(([dc], self.freq_bands, [nyquist]))
        
        # for each wall extrapolate coeffs to 0 Hz and Nyquist            
        return np.array([self._extrapolate_band(i) for i in range(len(self.materials_coeffs))])
       
    def _extrapolate_band(self, i):
        wall_coeffs = self.materials_coeffs[i]

        max_value = wall_coeffs[-1]
        min_value = wall_coeffs[0]
        
        return np.concatenate(([min_value], wall_coeffs, [max_value]))
            
    def _get_coefficients(self):
        """
        Given a list of material names get the corresponding values from the materials data.
        
        Returns:
        list: A 2D list of coefficients associated with each material name
        """
        coeffs_property = "coeffs"
        return np.array([np.array(self._find_value_by_key(self.materials, material, coeffs_property)) for _, material in self.walls_material.items()])    
    
    @staticmethod
    def _calc_air_absorption():
        pass
        
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
    
    
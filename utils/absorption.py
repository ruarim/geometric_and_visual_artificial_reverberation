from matplotlib import pyplot as plt
import numpy as np

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
    
    def __init__(self, walls_material: dict, data_dir: str, fs: float, temp_humidity='20C_50-70%'): # 20 Degress and 90% humidity on day of reference RIR recording
        self.temp_humidity = temp_humidity
        self.fs = fs
        self.materials: dict = read_json(data_dir)
        self.walls_material = walls_material
        self.freq_bands = np.array(self.materials["center_freqs"])
        self.coefficients = self._get_coefficients()
        self.coefficients_dict = self._get_coefficients_dict()
        self.air_absorption = self._get_air_absorption(self.temp_humidity)
        
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
        
        # air
        plt.plot(self.freq_bands, self.air_absorption, label=f"Air - {self.temp_humidity}")
        
        # walls
        for coefficients, wall in zip(self.coefficients, self.walls_material):
            plt.plot(self.freq_bands, coefficients, label=f"{wall} - {self.walls_material[wall]}")
        
        plt.legend()
                    
    def _get_coefficients(self):
        """
        Given a list of material names get the corresponding values from the materials data.
        
        Returns:
        list: A 2D list of coefficients associated with each material name
        """
        coeffs_property = "coeffs"
        return np.array([self._get_wall_coefficients(material, coeffs_property) for _, material in self.walls_material.items()])
    
    def _get_coefficients_dict(self):
        """
        Given a list of material names get the corresponding values from the materials data.
        
        Returns:
        dict: A dict with (key) wall name and (value) coefficients associated with each material name
        """
        coeffs_property = "coeffs"
        coeffs_dict = {}
        for wall_name, material in self.walls_material.items():
            coeffs_dict[wall_name] = self._get_wall_coefficients(material, coeffs_property)
        return coeffs_dict
    
    def _get_wall_coefficients(self, material_name, coeffs_property):
        coeffs = self._find_value_by_key(self.materials, material_name, coeffs_property)
        self._extrapolate(coeffs)
        return np.array(coeffs)
    
    def _extrapolate(self, values: list[float]):
        """
        If only 6 bands of coefficients, extend the coefficents by duplicating the last value.
        """
        num_bands = len(self.freq_bands)
        if len(values) == num_bands: return values
        if len(values) < num_bands: 
            return values.append(values[-1])
        else: f'ERROR: Invalid number of coefficients length: {len(values)}'

        
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
    
    
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import numpy as np
from pyroomacoustics.experimental.rt60 import measure_rt60

from config import RoomConfig

class ImageSourceMethod:
    def __init__(self, room_config: RoomConfig, fs=44100):
        self.room_dims = room_config.ROOM_DIMS
        self.absorption = room_config.WALL_MATERIALS
        self.source = room_config.SOURCE_LOC
        self.mic = room_config.MIC_LOC
        self.order = room_config.ER_ORDER
        self.fs = fs
    
    
    def _make_room_shoebox(self, room_dims, max_order, source, mic):
        """
        A short helper function to make the room according to config
        """
        materials = pra.make_materials(
            ceiling=(self.absorption['ceiling'], 0.0),
            floor=(self.absorption['floor'], 0.0),
            east=(self.absorption['east'], 0.0),
            west=(self.absorption['west'], 0.0),
            north=(self.absorption['north'], 0.0),
            south=(self.absorption['south'], 0.0),
        )
        
        shoebox = (
            pra.ShoeBox(
                room_dims,
                fs=self.fs,
                materials=materials,
                max_order=max_order,
                air_absorption=True,
            )
            .add_source(source)
            .add_microphone(mic)
        )

        return shoebox
    
    def process(self, order=0, norm=False, plot_rt60=False, rt60_theory_type='sabine'):
        """
        Render the room impulse response of the given geometery and materials
        """
        shoebox = self._configure_shoebox(order)
        
        # run image source method and render rir
        shoebox.image_source_model()
        shoebox.compute_rir()
         
        # copy to local memory
        rir = shoebox.rir[0][0].copy()
        
        if plot_rt60:
            rt60_theory = shoebox.rt60_theory(formula=rt60_theory_type)
            
            plt.figure(figsize=(10, 4))
            
            rt60_measured = measure_rt60(rir, fs=self.fs, plot=True, rt60_tgt=rt60_theory)
            
            print(f'RT60 Measured: {rt60_measured}')
            print(f'RT60 Theory: {rt60_theory}')
        
        if(norm): rir = rir / np.max(rir)
        
        return rir
        
    def get_source_coords(self, plot=False, direct_path=False, order=0):
        """
        Method to find image source using pyroomacoustics C++ accelerated Image Source Method algorithm.

        return (list[list]): image sources in cartisian coordianates with the structure, x = image_source[0], y = image_source[1], z = image_source[2]
        """
        shoebox = self._configure_shoebox(order)
        
        # run image source method
        shoebox.image_source_model()
        
        # create copy of image sources from room engine
        image_sources = shoebox.room_engine.sources.copy()
                        
        # convert 2d list to list of x,y,z coords
        image_sources = self._to_coords_list(image_sources)
                
        # remove the original source
        if not direct_path:
            image_sources = list(filter(self._drop_source, image_sources))
            
        image_source_walls = [self._find_associated_wall(coords) for coords in image_sources]
        
        if plot:
            shoebox.plot()
        
        return image_sources, image_source_walls

    def _drop_source(self, var):
        """
        Remove the image source which matches the original source.
        Due to floating point number use find items that match in small decimal range
        """
        return not all(abs(a - b) < 1e-6 for a, b in zip(var, self.source))

    def _to_coords_list(self, image_sources):
        coord_list = [[image_sources[0, i], image_sources[1, i], image_sources[2, i]] for i in range(image_sources.shape[1])]
        return coord_list
    
    def _configure_shoebox(self, order):
        if(order == 0):
            return self._make_room_shoebox(self.room_dims, self.order, self.source, self.mic)
        else: # overide object wide reflection order
            return self._make_room_shoebox(self.room_dims, order, self.source, self.mic)
    
    def _find_associated_wall(self, image_source):
        x, y, z = image_source
        Lx, Ly, Lz = self.room_dims
        
        if x < 0:
            return "west"
        elif x > Lx:
            return "east"
        elif y < 0:
            return "north"
        elif y > Ly:
            return "south"
        elif z < 0:
            return "floor"
        elif z > Lz:
            return "ceiling"
        else:
            return "inside room"
    
    def _find_intersection(image_source, receiver, boundary_axis, boundary_value):
        """
        Find the intersection of the path from the image source to the receiver with a given boundary.
        
        Parameters:
        image_source (list): Coordinates of the image source (x, y, z).
        receiver (list): Coordinates of the receiver (x, y, z).
        boundary_axis (str): Axis of the boundary ('x', 'y', 'z').
        boundary_value (float): Value of the boundary along the given axis.
        
        Returns:
        list[float]: Coordinates of the reflection point on the boundary.
        """
        x_s, y_s, z_s = image_source
        x_r, y_r, z_r = receiver
        
        if boundary_axis == 'x':
            t = (boundary_value - x_s) / (x_r - x_s)
            y_reflect = y_s + t * (y_r - y_s)
            z_reflect = z_s + t * (z_r - z_s)
            return [boundary_value, y_reflect, z_reflect]
        
        elif boundary_axis == 'y':
            t = (boundary_value - y_s) / (y_r - y_s)
            x_reflect = x_s + t * (x_r - x_s)
            z_reflect = z_s + t * (z_r - z_s)
            return [x_reflect, boundary_value, z_reflect]
        
        elif boundary_axis == 'z':
            t = (boundary_value - z_s) / (z_r - z_s)
            x_reflect = x_s + t * (x_r - x_s)
            y_reflect = y_s + t * (y_r - y_s)
            return [x_reflect, y_reflect, boundary_value]
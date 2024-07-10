import pyroomacoustics as pra
import matplotlib.pyplot as plt
from config import RoomConfig
# @TODO refactor into class

class ImageSourceMethod:
    def __init__(self, room_config: RoomConfig):
        self.room_dims = room_config.ROOM_DIMS
        self.source = room_config.SOURCE_LOC
        self.mic = room_config.MIC_LOC
        self.order = room_config.ER_ORDER
    
    
    def make_room(self, room_dims, max_order, source, mic):
        """
        A short helper function to make the room according to config
        """
        shoebox = (
            pra.ShoeBox(
                room_dims,
                max_order=max_order,
                ray_tracing=False,
                air_absorption=True,
            )
            .add_source(source)
            .add_microphone(mic)
        )

        return shoebox

    def run(self, show=False):
        """
        Method to find image source using pyroomacoustics C++ accelerated Image Source Method algorithm.

        return (list[list]): image sources in cartisian coordianates with the structure, x = image_source[0], y = image_source[1], z = image_source[2]
        """
        shoebox = self.make_room(self.room_dims, self.order, self.source, self.mic)
        
        # run image source method
        shoebox.image_source_model()
        
        # create copy of image sources from room engine
        image_sources = shoebox.room_engine.sources.copy()
            
        # convert 2d list to list of x,y,z coords
        image_sources = self.to_coords_list(image_sources)
                
        # remove  the original source
        image_sources = list(filter(self.drop_source, image_sources))
        
        if show: 
            shoebox.plot()  
            plt.show()
        
        return image_sources

    def drop_source(self, var):
        """
        Remove the image source which matches the original source.
        Due to floating point number use find items that match in small decimal range
        """
        return not all(abs(a - b) < 1e-6 for a, b in zip(var, self.source))

    def to_coords_list(self, image_sources):
        coord_list = [[image_sources[0, i], image_sources[1, i], image_sources[2, i]] for i in range(image_sources.shape[1])]
        return coord_list

    def find_intersection(image_source, receiver, boundary_axis, boundary_value):
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
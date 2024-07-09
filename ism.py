import pyroomacoustics as pra
import matplotlib.pyplot as plt

from config import CONFIG

def make_room(room_dims, max_order, source, mic, fs):
    """
    A short helper function to make the room according to config
    """
    shoebox = (
        pra.ShoeBox(
            room_dims,
            fs=fs,
            max_order=max_order,
            ray_tracing=False,
            air_absorption=True,
        )
        .add_source(source)
        .add_microphone(mic)
    )

    return shoebox

def image_source_method(config, show=False):
    """
    Method to find image source using pyroomacoustics C++ accelerated Image Source Method algorithm.

    return (list[list]): image sources in cartisian coordianates with the structure, x = image_source[0], y = image_source[1], z = image_source[2]
    """
    shoebox = make_room(config["ROOM_DIMS"], 
                        config["ER_ORDER"], 
                        config["SOURCE_LOC"], 
                        config["MIC_LOC"], 
                        config["FS"],
    )
    
    shoebox.image_source_model()
    image_source = shoebox.room_engine.sources.copy()
    
    if show: 
        shoebox.plot()  
        plt.show()
    
    return image_source
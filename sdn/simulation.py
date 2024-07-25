import numpy as np

# classes and utilites
from utils.point3D import Point3D
from .network import Network
from .room import Room
from .performance import Performance

def run_sdn_simulation(signal_in, room_dims, source_loc, mic_loc, er_order, flat_absorption, fs, direct_path=True):
    signal_out = np.zeros_like(signal_in)
    # setup the delay network
    source_location = Point3D(source_loc)
    mic_location = Point3D(mic_loc)
    room = Room(room_dims, source_location, mic_location, er_order) 
    sdn = Network(room.early_reflections, source_location, mic_location, flat_absorption, fs, direct_path) 

    # run the simulation
    for s in range(len(signal_in)):
        # process the current sample
        sample = signal_in[s]
        sample_out = sdn.process(sample)  
        # model mic orientation with left right gain - use microphone array instead
        signal_out[s] = sample_out
        # print(f"processing sample: {s}")
    
    return signal_out
    

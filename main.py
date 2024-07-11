import numpy as np
from matplotlib import pyplot as plt
from scipy.linalg import hadamard
from math import sqrt

from config import SimulationConfig, RoomConfig, TestSignalConfig, OutputConfig
from ism import ImageSourceMethod
from early_reflections import EarlyReflections
# from late_reverberation import LateReveberation - refactor fdn here
from utils.signals import signal
from utils.point3D import Point3D
from utils.plot import plot_comparision, plot_signal
from utils.reverb_time import ReverbTime
from fdn import FeedbackDelayNetwork

# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_signal_config = TestSignalConfig()
output_config = OutputConfig()

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config, fs=simulation_config.FS) # pass specific config values instead
image_source_coords = ism.get_source_coords(show=False)
image_source_points = [Point3D(image_source) for image_source in image_source_coords]
source_point = Point3D(room_config.SOURCE_LOC)
mic_point = Point3D(room_config.MIC_LOC)

# tapped delay line or render ism and convolve with input
er = EarlyReflections(source_point,  
                      mic_point, 
                      image_source_points, 
                      simulation_config,
                      room_config,
)

# refactor into late_reverberation class
reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.sabine_eyring_t60()

fdn_delay_times = [809, 877, 937, 1049, 1151, 1249, 1373, 1499]
b = np.ones_like(fdn_delay_times)
c = np.ones_like(fdn_delay_times)
matrix = hadamard(len(fdn_delay_times)) / sqrt(len(fdn_delay_times))  # unitary matrix: normalise to the square root of num delays


fdn = FeedbackDelayNetwork(b, 
                           c, 
                           matrix, 
                           fdn_delay_times, 
                           simulation_config.FS, 
                           rt60_flat=rt60_sabine, 
                           lossless=False,
)

# run simulation
input_signal = signal("unit", simulation_config.SIGNAL_LENGTH, simulation_config.FS)
output_signal = np.zeros_like(input_signal)

er_signal = er.process(input_signal, output_signal, type='tdl')
# TODO: Fix stability for non impulse signal
lr_signal = [fdn.process(sample) for sample in er_signal]

# create propigation lines for each image source -> mic

# scatter the output of the progigation lines

# use BRDF - specular reflections go to FDN, scattering goes to mic.

# feed output of scattering to a feedback delay network

# output summation of scattering

# pyroomacoustics rir

ism_rir = ism.render()

# plot
compare_data = {
        "FDN": lr_signal,
        'PyRoom': ism_rir,
        'TappedDelayLine': er_signal,
}

xlim = [0, 1000]
plot_comparision(compare_data, 'Early Reflections - Tapped Delay Line', xlim=xlim)
plot_signal(ism_rir, title="Image Source Method RIR", xlim=xlim)
plot_signal(output_signal, 'Early Reflections - Tapped Delay Line', xlim=xlim)
plot_signal(lr_signal, "Late Reflections - FDN")
plt.show()
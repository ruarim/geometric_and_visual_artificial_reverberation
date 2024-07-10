import numpy as np
from matplotlib import pyplot as plt

from config import SimulationConfig, RoomConfig, TestSignalConfig, OutputConfig
from ism import ImageSourceMethod
from early_reflections import EarlyReflections
# from late_reverberation import LateReveberation
from utils.signals import signal
from utils.point3D import Point3D
from utils.plot import plot_comparision, plot_signal

# Create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_signal_config = TestSignalConfig()
output_config = OutputConfig()

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config) # pass specific config values instead
image_sources = ism.run(show=False)
image_sources_points = [Point3D(image_source) for image_source in image_sources]

source_point = Point3D(room_config.SOURCE_LOC)
mic_point = Point3D(room_config.MIC_LOC)

# tapped delay line or render ism and convolve with input
er = EarlyReflections(source_point,  
                      mic_point, 
                      image_sources_points, 
                      simulation_config,
)

# fdn
# late_reverberation = FDN()

# run simulation
input_signal = signal("unit", simulation_config.SIGNAL_LENGTH,  simulation_config.FS)
output_signal = np.zeros_like(input_signal)

output_signal = er.process(input_signal, output_signal, type='tdl')

# create propigation lines for each image source -> mic

# scatter the output of the progigation lines

# use BRDF - specular reflections go to FDN, scattering goes to mic.

# feed output of scattering to a feedback delay network

# output summation of scattering

# plot
compare_data = {
        'Input': input_signal,
        'Output': output_signal,
}
# plot_comparision(compare_data, 'Early Reflections - Tapped Delay Line', xlim=[0,70])

plot_signal(output_signal, 'Early Reflections - Tapped Delay Line', xlim=[0,70])
plt.show()
import numpy as np
from matplotlib import pyplot as plt
from utils.matrix import scaled_hadamard # refactor to class
from utils.matlab import init_matlab_eng

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from early_reflections.ism import ImageSourceMethod
from early_reflections.early_reflections import EarlyReflections
# from late_reverberation import LateReveberation - refactor fdn here
from utils.signals import signal
from utils.point3D import Point3D
from utils.plot import plot_comparision, plot_signal
from utils.reverb_time import ReverbTime
from utils.file import write_array_to_wav
from late_reverberation.fdn import FeedbackDelayNetwork

# create instances of config classes
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

# find image sources up to Nth order 
ism = ImageSourceMethod(room_config, fs=simulation_config.FS) # pass specific config values instead
ism_er_rir = ism.render(norm=True) # rendering early reflections with pyroomacoustics ism
image_source_coords = ism.get_source_coords(show=False)
image_source_coords_2nd = ism.get_source_coords(show=False, order=2)

image_source_points = [Point3D(image_source) for image_source in image_source_coords]
source_point = Point3D(room_config.SOURCE_LOC)
mic_point = Point3D(room_config.MIC_LOC)

# tapped delay line or render ism and convolve with input
er = EarlyReflections(source_point,  
                      mic_point, 
                      image_source_points, 
                      simulation_config,
                      room_config,
                      ism_rir=ism_er_rir,
)

# refactor into late_reverberation class
reverb_time = ReverbTime(room_config)
rt60_sabine, rt60_eyring = reverb_time.rt60s()

fdn_delay_times = np.array([809, 877, 937, 1049, 1151, 1249, 1373, 1499]) # log distributed prime numbers, TODO: mutual prime around mean free path
b = np.ones_like(fdn_delay_times)
c = np.ones_like(fdn_delay_times)
matrix = scaled_hadamard(len(fdn_delay_times))  # unitary matrix: normalise to the square root of num delays

# run simulation
input_signal = signal(
        test_config.SIGNAL_TYPE, 
        simulation_config.SIGNAL_LENGTH, 
        simulation_config.FS, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME
)

output_signal = np.zeros_like(input_signal)

er_signal_tdl = er.process(input_signal, output_signal, type='tdl')

er_signal_convolve = er.process(input_signal, output_signal, type='convolve')

# start matlab process
matlab_eng = init_matlab_eng()

lr_signal = np.array(matlab_eng.velvet_fdn(er_signal_tdl, fdn_delay_times, simulation_config.FS))

# end matlab process
matlab_eng.quit()

# mono for now
full_ir = np.array([er + lr[0] for er, lr in zip(er_signal_tdl, lr_signal)])

# render pyroomacoustics rir for comparison
ism_full_rir = ism.render(order=80)

config_str = f'ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}'

if(output_config.OUTPUT_TO_FILE):
        # output early reflections RIR
        write_array_to_wav(test_config.ER_RIR_DIR, test_config.SIGNAL_TYPE, er_signal_tdl, simulation_config.FS)
        write_array_to_wav(test_config.FULL_RIR_DIR, f"{config_str}", full_ir, simulation_config.FS)
# plot
compare_data = {
        # "Full ISM": ism_full_rir / np.max(ism_full_rir),
        # "Convolution": er_signal_convolve,
        "Full RIR": full_ir,
        'Tapped Delay Line': er_signal_tdl,
        "Velvet FDN": lr_signal,
}
     
xlim = None
y_offset = np.max(full_ir) + np.abs(np.min(full_ir))
plot_comparision(
        compare_data, 
        f'ISM-FDN RIR, ER Order: {room_config.ER_ORDER}, Room Dimensions: {room_config.ROOM_DIMS}', 
        xlim=xlim, 
        plot_time=True, 
        y_offset=y_offset
)

# plot_signal(ism_full_rir, title="Image Source Method RIR", xlim=xlim)
# plot_signal(output_signal, 'Early Reflections - Tapped Delay Line', xlim=xlim)
# plot_signal(lr_signal, "Late Reflections - FDN")
# plot_signal(full_ir, "Full IR")
plot_signal(full_ir, fs=simulation_config.FS, xlim=xlim, plot_time=True)
plt.show()
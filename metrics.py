import numpy as np
from matplotlib import pyplot as plt
from librosa import power_to_db
from os import listdir

from utils.signals import signal
from utils.plot import plot_comparison, plot_signal, plot_spectrogram
from config import RoomConfig, TestConfig
from utils.reverb_time import ReverbTime
from evaluation.echo_density import echo_density
from evaluation.modal_density import modal_density

def rms_diff():
    pass

# configs
room_config = RoomConfig()
test_config = TestConfig()
reverb_time = ReverbTime(room_config)

def get_rir(dir, file, norm=True):        
    name = file[:len(file)-4]
    rir, fs = signal('file', file, data_dir=dir, file_name=file)
    if norm: rir = rir / np.max(np.abs(rir))
    return {"name": name, "rir": rir, "fs": fs}

rir_dir   = test_config.FULL_RIR_DIR
rir_files = listdir(rir_dir)
rir_files = [file for file in rir_files if file.endswith('.wav')]
rirs      = [get_rir(rir_dir, file) for file in rir_files]

blacklist = [
    'Hadamard FDN - 16 ISM delays - one pole', 
    'Image Source Method - 150th order'
]

comparison = {}
for rir in rirs:
    name  = rir['name']
    if name in blacklist: continue
    
    audio = rir['rir']
    comparison[name] = audio

xlim = [0, 0.1]
y_offset = 2
plot_comparison(comparison, xlim=[0, 0.1])

# loop and add to dict 
for rir in rirs:
    name  = rir['name']
    audio = rir['rir'] # rename h
    fs    = rir['fs']
    rt60_bands = reverb_time.analyse_rt60_bands(audio, fs)
    
    ed = echo_density(audio, fs, truncate=True, plot=True, name=name)
    plt.xlim([0, 0.5 * fs])
    
    num_modes, md, is_shroeder_min = modal_density(audio, fs, name=name, band=500, rt60=rt60_bands[500.0])
    
    rir['rt60_bands'] = rt60_bands
    rir["echo_density"] = ed
    rir["modal_density"] = md
    rir["num_modes"] = num_modes
    rir['is_shroeder_min'] = is_shroeder_min
    
# get rms diff of metrics from real rir

# energy decay relief 

# early decay time use -10 instead of -60 in rt60 measurment

plt.show()
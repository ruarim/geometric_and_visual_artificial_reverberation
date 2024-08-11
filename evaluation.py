import numpy as np
from matplotlib import pyplot as plt
from librosa import power_to_db
from pyroomacoustics.experimental.rt60 import measure_rt60
from pyroomacoustics.acoustics import OctaveBandsFactory
from os import listdir

from utils.signals import signal
from utils.plot import plot_comparison, plot_signal, plot_spectrogram
from config import RoomConfig, TestConfig
from utils.reverb_time import ReverbTime
from utils.echo_density import echo_density

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

# instead loop and add to dict 
for rir in rirs:
    name = rir['name']
    audio = rir['rir']
    fs = rir['fs']
    rt60_bands = reverb_time.analyse_rt60_bands(audio, fs)
    rir['rt60_bands']   = rt60_bands
    rir["echo_density"] = echo_density(audio, fs, truncate=True)

    # echo density
    plt.figure(figsize=(10, 4))
    plt.title(f'echo density {name}')
    plt.plot(rir["echo_density"])
    
    # modal density
 
# print(rirs[0])

# energy decay curve 

# energy decay relief 

# mode density

# early decay time

plt.show()
import numpy as np
from os import listdir
from random import randrange

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.signals import signal
from utils.file import write_array_to_wav

from rirs import rirs_config

from utils.convolve import fft_convolution

# config dataclasses
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

# set of anechoic audio
samples_dir = test_config.SAMPLES_DIR
anechoic_files = listdir(samples_dir)
anechoic_files = [file for file in anechoic_files if file.endswith('.wav')]

# create all stimuli for listening test
stimuli_dir = test_config.STIMULI_DIR
rir_dir = test_config.FULL_RIR_DIR


_, prev_fs = signal(
    "file", 
    data_dir=samples_dir, 
    file_name=anechoic_files[0]
)

def get_rirs(fs):
    # get the real room impulse response for reference.
    real_rir_file = test_config.REAL_RIR_FILE
    real_rir, real_fs  = signal(
            'file', 
            data_dir=test_config.ROOM_DIR, 
            file_name=real_rir_file,
    )
    
    rirs = rirs_config(fs)
    rirs.append({
        'name': "Small Hallway",
        'rir': real_rir,
    })

rirs = get_rirs(prev_fs)

# add the real rir

# generate RIR and apply to target audio
for file in anechoic_files:
    anechoic_audio, fs = signal(
        'file', 
        data_dir=samples_dir, 
        file_name=file,
        padding=0.5
    )
    
    # recompute rirs if sampling rate changes
    if(fs != prev_fs):
        rirs = get_rirs(fs)
    
    file_name = file[:len(file)-4]
    # for audio files
    for rir in rirs:
        name = rir['name']
        rir  = rir['rir']

        if isinstance(rir, tuple):
            print('not signal')
            continue
                        
        random_order = randrange(0, 100)
        stimulus = fft_convolution(anechoic_audio, rir, norm=True)
        
        # normalise loudness (db)
        
        # output processed audio
        write_array_to_wav(
            f"{stimuli_dir}/{file_name}", 
            f"{random_order}_{name}_{file_name}", 
            stimulus, 
            fs, 
            time_stamp=False
        )
    
        print(f'Saved {name} - {file}')
        
    prev_fs = fs
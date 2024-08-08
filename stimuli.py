import numpy as np
from os import listdir

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.signals import signal
from utils.file import write_array_to_wav

from ism_fdn import ISMFDN
from standard_fdn import StandardFDN
from sdn import SDN
from early_reflections.ism import ImageSourceMethod

from utils.convolve import fft_convolution

# create a config to pass to each simulation class

# config dataclasses
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()

def rirs_config(fs):
    print(f'Synthesising RIRs, sample rate: {fs}')
    unit_impulse, _ = signal(
        'unit', 
        simulation_config.SIGNAL_LENGTH, 
        fs, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
    )
    return [
        {
            'name': "ISMFDN Parallel - all ISM delays",
            'processor': ISMFDN(
                fs, 
                simulation_config, 
                room_config, 
                fdn_N=-1, 
                processing_type='parallel'
            ).process(unit_impulse),
        },
        {
            'name': "ISMFDN Parallel - 16 ISM delays",
            'processor': ISMFDN(
                fs, 
                simulation_config, 
                room_config, 
                fdn_N=16, 
                processing_type='parallel'
            ).process(unit_impulse),
        },
        {
            'name': "Hadamard FDN - 16 ISM delays",
            'processor': ISMFDN(
                fs, 
                simulation_config, 
                room_config, 
                fdn_N=16, 
                processing_type='fdn_only'
            ).process(unit_impulse),
        },
        {
            'name': "SDN",
            'processor': SDN(
                fs, 
                simulation_config, 
                room_config
            ).process(unit_impulse),
        },
        # {
        #     'name': "Standard FDN - 8 delays",
        #     'processor': StandardFDN(
        #         fs,
        #         simulation_config, 
        #         room_config
        #     ).process(input_signal),
        # },
        {
            'name': 'Image Source Method - 150th order',
            'processor': ImageSourceMethod(
                room_config, 
                fs=fs
            ).process(order=150),
        },
        {
            'name': 'Small Hallway RIR',
            'processor': signal(
                'file', 
                data_dir='_rooms/', 
                file_name=test_config.REAL_RIR_FILE,
            )[0]
        }
    ]

samples_dir = test_config.SAMPLES_DIR
# set of anechoic audio
anechoic_files = listdir(samples_dir)

# create all stimuli for listening test
stimuli_folder = '_output/stimuli/'

prev_fs = signal(
    "file", 
    data_dir=samples_dir, 
    file_name=anechoic_files[0]
)

rirs = rirs_config(prev_fs)

for file in anechoic_files:
    if file[len(file)-4:] != '.wav': continue
    
    anechoic_audio, fs = signal(
        'file', 
        data_dir=samples_dir, 
        file_name=file,
    )
    
    # recompute rirs if sampling rate changes
    if(fs != prev_fs):
        rirs = rirs_config(fs)
    
    file_name = file[:len(file)-4]
    # for audio files
    for reverb in rirs:
        name = reverb['name']
        rir  = reverb['processor']

        if not isinstance(rir, tuple):
            stimulus = fft_convolution(anechoic_audio, rir, norm=True)
            write_array_to_wav(stimuli_folder, f"{name}_{file_name}", stimulus, fs)
        else:
            for rir, i in zip(rir, range(len(rir))):
                stimulus = fft_convolution(anechoic_audio, rir, norm=True)
                write_array_to_wav(stimuli_folder, f'{name}_{i+1}_{file_name}', stimulus, fs)
                
        print(f'Saved {name} - {file}')
        
    prev_fs = fs
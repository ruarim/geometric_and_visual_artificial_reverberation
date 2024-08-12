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
from evaluation.rms_difference import rms_diff
from utils.matlab import init_matlab_eng

# configs
room_config = RoomConfig()
test_config = TestConfig()
reverb_time = ReverbTime(room_config)

# plot the results of the evaluation
def plot_results(metric, metric_name, title):
    names = list(metric.keys())
    values = list(metric.values())
        
    plt.figure(figsize=(10, 6))
    bars = plt.bar(names, values)

    plt.xlabel('Room Impulse Response')
    plt.ylabel(f'{metric_name}')
    plt.title(f'{title}')
    plt.xticks(rotation=45) 
    
    # add values to bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, round(yval, 3), ha='center', va='bottom')

def get_rir(dir, file, norm=True):        
    name = file[:len(file)-4]
    rir, fs = signal('file', file, data_dir=dir, file_name=file)
    if norm: rir = rir / np.max(np.abs(rir))
    return {
        "name": name, 
        "rir": rir, 
        "fs": fs,
    }

def get_rirs_for_evaluation(test_config: TestConfig):
    rir_dir   = test_config.FULL_RIR_DIR
    rir_files = listdir(rir_dir)
    rir_files = [file for file in rir_files if file.endswith('.wav')]
    rirs      = [get_rir(rir_dir, file) for file in rir_files]
    
    return rirs

def evaluate(fs, h, name, matlab_eng):
    rt60_bands = reverb_time.analyse_rt60_bands(h, fs)
    
    ed, t_mix = echo_density(
        h,
        fs, 
        matlab_eng,
        truncate_start=False, 
        plot=True,
        name=name,
    )
    
    num_modes, md, is_shroeder_min = modal_density(
        h, 
        fs, 
        name=name, 
        band=500, 
        rt60=rt60_bands[500.0]
    )
    
    return {
        'rt60_bands': rt60_bands,
        "echo_density": ed,
        't_mix': t_mix,
        "modal_density": md,
        "num_modes": num_modes,
        'is_shroeder_min': is_shroeder_min,
    }
    
matlab_eng = init_matlab_eng()

# get the real room impulse response for reference.
real_rir_file = test_config.REAL_RIR_FILE
real_rir, real_fs  = signal(
        'file', 
        data_dir=test_config.ROOM_DIR, 
        file_name=real_rir_file,
)

real_rir = {
    "name": real_rir_file[:len(real_rir_file)-4], 
    "rir": real_rir, 
    "fs": real_fs, 
}

real_rir['evaluation'] = evaluate(
    real_rir['fs'], 
    real_rir['rir'], 
    real_rir['name'],
    matlab_eng
)
    
rirs = get_rirs_for_evaluation(test_config)   
    
blacklist = [
    'Hadamard FDN - 16 ISM delays - one pole', 
    'Image Source Method - 150th order'
]

comparison = {}
for rir in rirs:
    name  = rir['name']
    if name in blacklist: continue
    
    h = rir['rir']
    comparison[name] = h

xlim = [0, 0.1]
y_offset = 2
plot_comparison(comparison, xlim=[0, 0.1])

# loop and add to dict 
for rir in rirs:
    name = rir['name']
    h = rir['rir']
    fs = rir['fs']
    rt60_bands = reverb_time.analyse_rt60_bands(h, fs)
    
    rir['evaluation'] = evaluate(fs, h, name, matlab_eng) 
    
# get rms diff of metrics from real rir

# energy decay relief 

# early decay time use -10 instead of -60 in rt60 measurment

# find rms difference between real rir and synthesised metrics.
rms_diffs = {}
real_rir_eval = real_rir['evaluation']

for rir in rirs:
    rir_name = rir['name']
    rir_eval = rir['evaluation']
   
    # number of modes
    rmsd_num_modes = rms_diff(
        rir_eval['num_modes'], 
        real_rir_eval['num_modes'],
    )
    if 'num_modes' not in rms_diffs:
        rms_diffs['num_modes'] = {}
    rms_diffs['num_modes'][rir_name] = rmsd_num_modes

    # modal density
    rmsd_md = rms_diff(
        rir_eval['modal_density'], 
        real_rir_eval['modal_density'],
    )
    if 'modal_density' not in rms_diffs:
        rms_diffs['modal_density'] = {}
    rms_diffs['modal_density'][rir_name] = rmsd_md
    
    # RT60 at 500 Hz
    rmsd_rt60_500Hz = rms_diff(
        rir_eval['rt60_bands'][500.0], 
        real_rir_eval['rt60_bands'][500.0],
    )
    if 'rt60_500Hz' not in rms_diffs:
        rms_diffs['rt60_500Hz'] = {}
    rms_diffs['rt60_500Hz'][rir_name] = rmsd_rt60_500Hz
    
    # Mixing Time
    rmsd_rt60_500Hz = rms_diff(
        rir_eval['t_mix'], 
        real_rir_eval['t_mix'],
    )
    if 't_mix' not in rms_diffs:
        rms_diffs['t_mix'] = {}
    rms_diffs['t_mix'][rir_name] = rmsd_rt60_500Hz
    
for metric in rms_diffs:
    plot_results(rms_diffs[metric], metric, f'Root Mean Squared difference: {metric}')
    
plt.show()

matlab_eng.quit()
import numpy as np
from matplotlib import pyplot as plt
from librosa import power_to_db
from os import listdir
import textwrap

from utils.signals import signal
from utils.plot import plot_comparison, plot_signal, plot_spectrogram
from config import RoomConfig, TestConfig, SimulationConfig
from utils.reverb_time import ReverbTime
from evaluation.echo_density import echo_density
from evaluation.modal_density import modal_density
from evaluation.rms_difference import rms_diff
from utils.matlab import init_matlab_eng
from utils.absorption import Absorption

# configs
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
reverb_time = ReverbTime(room_config)
absorption = Absorption(
    room_config.WALL_MATERIALS, 
    room_config.MATERIALS_DIR, 
    simulation_config.FS
)

def plot_bar_chart(metric, metric_name, title):
    # Sort the metric dictionary by values (RMS differences) in ascending order
    metric = dict(sorted(metric.items(), key=lambda item: item[1], reverse=False))
    names = list(metric.keys())
    values = list(metric.values())

    # Normalize values: inverse scaling since smaller RMS is better
    min_value = min(values)
    max_value = max(values)
    norm_values = [(max_value - val) / (max_value - min_value) for val in values]
    
    # Set colors: 
    colors = ['tab:green' if name.startswith('ISMFDN, FIR') else
              'tab:orange' if name.startswith('ISMFDN, One-pole') else
              'lightgray' 
              for name in names]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(len(names)), values, color=colors)

    plt.ylabel(f'Model Performance (1 = Best)')
    plt.title(f'{title}')
    
    plt.xticks(range(len(names)), [textwrap.fill(name, width=20) for name in names], rotation=45, ha='right')
    
    # Adjust plot layout to make room for the rotated labels
    plt.tight_layout()

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

def evaluate(fs, h, name, matlab_eng, real_evaluation=None):
    rt60_bands_sabine, _ = reverb_time.rt60s_bands(
        absorption.coefficients + absorption.air_absorption,
        absorption.freq_bands,
    )
    rt60_bands = reverb_time.analyse_rt60_bands(h, fs)
    
    ed, t_mix = echo_density(
        h,
        fs, 
        matlab_eng,
        truncate_start=False, 
        plot=True,
        name=name,
        ref_ed=real_evaluation['echo_density'] if real_evaluation != None else [],
        ref_tmix=real_evaluation['t_mix'] if real_evaluation != None else 0,
    )
    
    num_modes, md, is_shroeder_min = modal_density(
        h, 
        fs, 
        name=name, 
        band=500, 
        rt60=rt60_bands[500.0],
    )
    
    return {
        'rt60_bands': rt60_bands,
        'rt60_bands_theory': rt60_bands_sabine,
        'echo_density': ed,
        't_mix': t_mix,
        'Modal Density 500 Hz': md,
        'Total Modes 500 Hz': num_modes,
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
    "rir": (real_rir * -1) / np.max(np.abs(real_rir)), 
    "fs": real_fs,
}

real_rir['evaluation'] = evaluate(
    real_rir['fs'], 
    real_rir['rir'], 
    'Small Hallway',
    matlab_eng,
)
real_rir_eval = real_rir['evaluation']
    
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
    
comparison['Small Hallway'] = real_rir['rir']

xlim = [0, 0.1]
y_offset = 2
plot_comparison(comparison, xlim=[0, 0.1])

# loop and add evaluation to dict 
for rir in rirs:
    name = rir['name']
    h = rir['rir']
    fs = rir['fs']
    rt60_bands = reverb_time.analyse_rt60_bands(h, fs)
    
    rir['evaluation'] = evaluate(fs, h, name, matlab_eng, real_evaluation=real_rir_eval)
    
# get rms diff of metrics from real rir

# energy decay relief 

# early decay time use -10 instead of -60 in rt60 measurment

# find rms difference between real rir and synthesised metrics.
rms_diffs = {}

for rir in rirs:
    rir_name = rir['name']
    rir_eval = rir['evaluation']
   
    # number of modes
    rmsd_num_modes = rms_diff(
        rir_eval['Total Modes 500 Hz'], 
        real_rir_eval['Total Modes 500 Hz'],
    )
    if 'Total Modes 500 Hz' not in rms_diffs:
        rms_diffs['Total Modes 500 Hz'] = {}
    rms_diffs['Total Modes 500 Hz'][rir_name] = rmsd_num_modes

    # modal density
    rmsd_md = rms_diff(
        rir_eval['Modal Density 500 Hz'], 
        real_rir_eval['Modal Density 500 Hz'],
    )
    if 'Modal Density 500 Hz' not in rms_diffs:
        rms_diffs['Modal Density 500 Hz'] = {}
    rms_diffs['Modal Density 500 Hz'][rir_name] = rmsd_md
    
    # RT60 at 500 Hz -  TODO: Use RT60 on the whole RIR instead
    rmsd_rt60_500Hz = rms_diff(
        rir_eval['rt60_bands'][500.0], 
        real_rir_eval['rt60_bands'][500.0],
    )
    if 'RT60 500Hz' not in rms_diffs:
        rms_diffs['RT60 500Hz'] = {}
    rms_diffs['RT60 500Hz'][rir_name] = rmsd_rt60_500Hz
    
    rt60f_diffs = []
    for rt60f_pred, rt60f_real in zip(rir_eval['rt60_bands'].values(), real_rir_eval['rt60_bands'].values()):
        rt60f_diff = rms_diff(
            rt60f_pred, 
            rt60f_real
        )
        rt60f_diffs.append(rt60f_diff)
    rt60f_mean_diff = sum(rt60f_diffs) / len(rt60f_diffs)
    
    if 'rt60_f' not in rms_diffs:
        rms_diffs['rt60_f'] = {}
    rms_diffs['rt60_f'][rir_name] = rt60f_mean_diff
    
    # Mixing Time
    rmsd_t_mix = rms_diff(
        rir_eval['t_mix'], 
        real_rir_eval['t_mix'],
    )
    if 't_mix' not in rms_diffs:
        rms_diffs['t_mix'] = {}
    rms_diffs['t_mix'][rir_name] = rmsd_t_mix
    
    rir['evaluation']['t_mix_diff'] = rmsd_t_mix
        
    # overall difference
    # normalise each difference between 0 - 1, diff / max diff
    
    # for metric in rms_diffs:
    #     diffs = []
    #     for rir in rms_diffs[metric].values():
    #         diffs.append()
                    
for metric in rms_diffs:
    plot_bar_chart(rms_diffs[metric], metric, f'{metric}')

rirs.append(real_rir)

blacklist = [
    'Hadamard FDN, One-pole, N=16', 
    'ISMFDN, FIR, N=24',
    'ISMFDN, One-pole, N=16',
]
# get mixing times
mixing_times_indices = []
max_t_mix_rms_diff = 0
min_t_mix_rms_diff = 0

for rir in rirs:
    name = rir['name']
    rir_eval = rir['evaluation']
    mixing_times_indices.append(rir_eval['t_mix'])
    if 't_mix_diff' in rir_eval:
        t_mix_rms_diff = rir_eval['t_mix_diff']
        if t_mix_rms_diff > max_t_mix_rms_diff:
            max_t_mix_rms_diff = t_mix_rms_diff
        if t_mix_rms_diff < min_t_mix_rms_diff:
            min_t_mix_rms_diff = t_mix_rms_diff
    
    
mixing_times_indices = np.concatenate(([0], [int(0.025 * fs)], mixing_times_indices, [int(0.125 * fs)]))
mixing_times_indices = np.sort(mixing_times_indices)

# time_diffs = np.diff(mixing_times_indices)
# normalised_diffs = 1 - (time_diffs / max(time_diffs))
# print(normalised_diffs)

colours = plt.cm.tab10(range(len(rirs)))
plt.figure(figsize=(10, 4)) 
plt.title('Early Echo Density')
time_vec = np.arange(len(real_rir['rir'])) / fs
# plt.plot(time_vec, real_rir['rir'], color='gray', label='Small Hallway RIR')

# Add horizontal line at 1
plt.axhline(y=1.0, color='black', linestyle='-', linewidth=1.5, label='Mixing Threshold')

for rir, colour in zip(rirs, colours):
    h = rir['rir']
    fs = rir['fs']
    name = rir['name']
    # if name in blacklist: continue
    
    evaluation = rir['evaluation']
    ed = evaluation['echo_density']

    t_mix_sec = round(evaluation['t_mix'] / fs, 3)
    ed = ed[mixing_times_indices]
    
    plt.plot(mixing_times_indices / fs, ed, marker='o', label=f'{name}', color=colour)

    max_width = 10
    min_width = 0.5
    # Adjust the height of the vertical line based RMS difference
    if 't_mix_diff' in evaluation:
        t_mix_diff = evaluation['t_mix_diff']
        diff_norm = (max_t_mix_rms_diff - t_mix_diff) / (max_t_mix_rms_diff - min_t_mix_rms_diff)
        line_width = min_width + (diff_norm) * (max_width - min_width)

        plt.axvline(x=t_mix_sec, ymin=0, ymax=diff_norm - 0.125, color=colour, linestyle='-', linewidth=line_width, zorder=1)
    else:
        plt.axvline(x=t_mix_sec, ymin=0, ymax=1 - 0.125, color=colour, linestyle='-', linewidth=max_width, zorder=1)

plot_times = mixing_times_indices / fs

# Set labels and ticks
plt.ylabel('Echo Density')
plt.xlabel('Time (secs)')
plt.xticks(plot_times, [f'{pt:.3f}' for pt in plot_times], rotation=45)
plt.xlim([mixing_times_indices[0] / fs, mixing_times_indices[-1] / fs])

# Move legend outside the graph
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
# plt.ylim([-0.25, 1.1])
plt.show()

# all rt60 on real spectrogram
plot_spectrogram(real_rir['rir'], rir['fs'], title=f'Small Hallway RIR Spectrogram with Reverb Times', y_scale='Log')

num_bands = len(absorption.freq_bands)
# plot real
rt60_bands_real = list(real_rir['evaluation']['rt60_bands'].values())

# plot sabine

# plot rirs
for rir, colour in zip(rirs, colours):
    name = rir['name']
    evalulation = rir['evaluation']
    rt60_bands = evalulation['rt60_bands']
    
    rt60_bands_arr = list(evalulation['rt60_bands'].values())
    
    # plot rerverb times
    rt60_analysis, = plt.plot(rt60_bands_arr[:num_bands], absorption.freq_bands, marker='o', label=f'{name}', color=colour)

plt.ylim([absorption.freq_bands[0] - 20, absorption.freq_bands[-1] + 750])
plt.xlim([0, 1.7])
plt.legend()

for rir in rirs:
    h = rir['rir']
    fs = rir['fs']
    name = rir['name']
    evalulation = rir['evaluation']
    
    plot_spectrogram(h, fs, title=f'{name} Spectrogram and Reverb Times', y_scale='Log')
    
    num_bands = len(absorption.freq_bands)
    rt60_bands_arr = list(evalulation['rt60_bands'].values())
    rt60_bands_real = list(real_rir['evaluation']['rt60_bands'].values())
    
    # plot rerverb times
    rt60_analysis, = plt.plot(rt60_bands_arr[:num_bands], absorption.freq_bands, marker='o', label=f'{name} RT60')
    rt60_sabine, = plt.plot(evalulation['rt60_bands_theory'][:num_bands], absorption.freq_bands, marker='o', label='Sabine RT60')
    rt60_real, = plt.plot(rt60_bands_real[:num_bands], absorption.freq_bands, marker='o', label='Real RT60')
    
    plt.ylim([absorption.freq_bands[0] - 20, absorption.freq_bands[-1] + 750])
    plt.xlim([0, 1.7]) 
    plt.legend(handles=[rt60_analysis, rt60_sabine, rt60_real])


plt.show()

matlab_eng.quit()
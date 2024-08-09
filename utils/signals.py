import numpy as np
from math import floor
from random import uniform
from utils.file import read_wav_file

def zeros(length):
    return np.zeros(length, dtype=np.float32) 

# generate a unit impulse
def unit_impulse(signal_length, gain):
    signal = zeros(signal_length)
    signal[0] = gain
    return signal

# generate a noise burst
def noise_burst(signal_length, burst_secs, fs, gain):
    burst_samples = floor(burst_secs * fs)
    signal = zeros(signal_length)
    
    for i in range(0, burst_samples): 
        signal[i] = uniform(-gain, gain)
        gain -= 1 / burst_samples
    
    return signal

# read a sample file
def file(data_dir, file_name):
    fs, data = read_wav_file(data_dir, file_name)
    return data, fs

# return fs depenant on signal type 
def signal(choice, signal_length=44100, fs=44100, burst_secs=0.1, gain=1.0, data_dir="", file_name="", channels=1):
    if choice == "unit":
        signal = unit_impulse(signal_length, gain)
    if choice == "noise":
        signal = noise_burst(signal_length, burst_secs, fs, gain)
    if choice == "file":
        signal, file_fs = file(data_dir, file_name)
        fs = file_fs
        # get mono
        if(channels == 1 and len(signal.shape) > 1): signal = [sample[0] for sample in signal] 
        # more general function fix for mono
        # if(channels != np.array(signal.shape)[1]): signal = [sample[:channels] for sample in signal] 
    # if "pulse": return pulse with pitch/harmonic content (sine, square, tri, saw...)
    
    # if len(signal) > signal_length: signal = signal[:signal_length]
    if channels > 1: return stack(signal, channels), fs
    else: return signal, fs

def stack(signal, n=2):
    return np.column_stack([signal] * n)
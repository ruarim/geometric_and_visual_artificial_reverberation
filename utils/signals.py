import numpy as np
from math import floor
from random import uniform
from utils.file import read_wav_file
from config import SIGNAL_LENGTH, FS

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
    return data

# return fs depenant on signal type 
def test_signal(choice, signal_length=SIGNAL_LENGTH, fs=FS,burst_secs=0.1, gain=1.0, data_dir="", file_name="", channels=1):
    if choice == "unit": 
        signal = unit_impulse(signal_length, gain)
    if choice == "noise": 
        signal = noise_burst(signal_length, burst_secs, fs, gain)
    if choice == "file": 
        signal = file(data_dir, file_name) # not returning fs for now
    # if "pulse": return pulse with harmonic content (sine, square, tri...)
    
    if channels > 1: return stack(signal, channels) 
    else: return signal

def stack(signal, n=2):
    return np.column_stack([signal] * n)
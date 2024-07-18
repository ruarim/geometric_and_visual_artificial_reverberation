import numpy as np
from matplotlib import pyplot as plt
from math import floor

def plot_signal(signal, title="", fs=44100, plot_time=False, xlim=None):
    plt.figure(figsize=(10, 4))
    plt.title(title)
    
    if plot_time: 
        time_vec = np.arange(len(signal)) / (fs / 1000)
        plt.plot(time_vec, signal)
        plt.xlabel('Time(ms)')
    else:
        plt.plot(signal) 
        plt.xlabel('Samples')
    
    plt.ylabel('Amplitude Linear')
    if(xlim != None): plt.xlim(xlim)
    
def plot_comparision(signals, title="", plot_time=False, fs=44100, xlim=None, y_offset=0.0):
    plt.figure(figsize=(10, 4))
    plt.title(title)
    count = 0
    for key in signals:
        signal = signals[key]
        signal += y_offset * count
        if plot_time:
            time_vec = np.arange(len(signal)) / (fs / 1000)
            plt.plot(time_vec, signal, label=key)
            plt.xlabel('Time(ms)')
        else: 
            plt.plot(signal, label=key)
            plt.xlabel('Samples')
        count+=1
    
    plt.ylabel('Amplitude Linear')
    plt.legend()
    plt.xlim(xlim)

def plot_frequnecy_response(y, title):
    X = linear_to_dB_norm(np.abs(np.fft.fft(y)))
    half_X = floor(len(X)/2)
    plt.figure(figsize=(10, 4))
    plt.title(title)
    plt.plot(X[:half_X])
    plt.ylabel('Magnitude (Normalised dB)')
    plt.xlabel('Frequency')

# normalised linear to dB conversion
def linear_to_dB_norm(x):
    epsilon = 1e-20
    x_max = np.max(x)
    return 20 * np.log10((x + epsilon) / x_max)

def show_plots():
    plt.show()
import numpy as np
from matplotlib import pyplot as plt
from math import floor
import librosa

def plot_signal(signal, title="", fs=44100, plot_time=False, xlim=None):
    plt.figure(figsize=(10, 4))
    plt.title(title)
    
    if plot_time: 
        time_vec = np.arange(len(signal)) / (fs)
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
            time_vec = np.arange(len(signal)) / (fs)
            plt.plot(time_vec, signal, label=key)
            plt.xlabel('Time(ms)')
        else: 
            plt.plot(signal, label=key)
            plt.xlabel('Samples')
        count+=1
    
    plt.ylabel('Amplitude Linear')
    plt.legend()
    plt.xlim(xlim)

def plot_frequnecy_response(y, fs, title="Frequency Spectrum (Db)"):
    X = linear_to_dB(np.abs(np.fft.fft(y)))
    plt.figure(figsize=(10, 4))
    plt.title(title)
    plt.plot(X[:floor(fs / 2)])
    plt.ylabel('Magnitude (Normalised dB)')
    plt.xlabel('Frequency')

def linear_to_dB(x):
    """
    Normalised linear to dB conversion
    """
    epsilon = 1e-20
    x_max = np.max(x)
    return 20 * np.log10((x + epsilon) / x_max)

def plot_spectrogram(y, sr, y_scale='linear', title="Spectrogram", xlim=None):    
    fig = plt.figure(figsize=(10, 4))
    plt.title(f'{title}')
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    img = librosa.display.specshow(D, y_axis=y_scale, x_axis='time', sr=sr)
    plt.ylabel(f"Frequency {y_scale} (Hz)")
    plt.xlabel("Time (secs)")
    plt.xlim(xlim)
    fig.colorbar(img, format="%+2.f dB")

def show_plots():
    plt.show()
    
# plot room dimension, source, mic, reflections
def plot_room(room_dimensions, source_pos, mic_pos, reflections=[]):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Room dimensions
    room_x, room_y, room_z = room_dimensions
    
    # Plotting the room
    # Floor
    ax.plot([0, room_x], [0, 0], [0, 0], color='k')
    ax.plot([0, room_x], [room_y, room_y], [0, 0], color='k')
    ax.plot([0, 0], [0, room_y], [0, 0], color='k')
    ax.plot([room_x, room_x], [0, room_y], [0, 0], color='k')

    # Ceiling
    ax.plot([0, room_x], [0, 0], [room_z, room_z], color='k')
    ax.plot([0, room_x], [room_y, room_y], [room_z, room_z], color='k')
    ax.plot([0, 0], [0, room_y], [room_z, room_z], color='k')
    ax.plot([room_x, room_x], [0, room_y], [room_z, room_z], color='k')

    # Vertical edges
    ax.plot([0, 0], [0, 0], [0, room_z], color='k')
    ax.plot([room_x, room_x], [0, 0], [0, room_z], color='k')
    ax.plot([0, 0], [room_y, room_y], [0, room_z], color='k')
    ax.plot([room_x, room_x], [room_y, room_y], [0, room_z], color='k')

    # Plot source position
    ax.scatter(source_pos[0], source_pos[1], source_pos[2], color='r', label='Source')

    # Plot microphone position
    ax.scatter(mic_pos[0], mic_pos[1], mic_pos[2], color='b', label='Microphone')

    # Plot reflections
    reflections = np.array(reflections)
    if reflections.size > 0:
        ax.scatter(reflections[:, 0], reflections[:, 1], reflections[:, 2], color='g', label='Early Reflections')

    # Labels and limits
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    ax.set_xlim([0, room_x])
    ax.set_ylim([0, room_y])
    ax.set_zlim([0, room_z])

    # Manually set tick marks for even scaling
    ax.set_xticks(np.arange(0, room_x + 1, 1))
    ax.set_yticks(np.arange(0, room_y + 1, 1))
    ax.set_zticks(np.arange(0, room_z + 1, 1))

    # Set aspect ratio to be equal
    ax.set_box_aspect([room_x, room_y, room_z])  # Aspect ratio is 1:1:1

    ax.legend()
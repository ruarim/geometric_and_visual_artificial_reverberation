from scipy.io.wavfile import write, read
import scipy.io
from datetime import datetime
from os import path 
import numpy as np
import warnings

def read_wav_file(data_dir: str, file_name: str): 
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", scipy.io.wavfile.WavFileWarning)
        
        # construct the path to the WAV file.
        wav_fname = path.join(data_dir, file_name)

        # read the WAV file.
        fs, data = scipy.io.wavfile.read(wav_fname)
    
    # determine the bit depth of the data and normalize it to the range [-1, 1].
    if data.dtype == np.int16:
        data = data.astype(np.float32) / np.iinfo(np.int16).max
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / np.iinfo(np.int32).max
    elif data.dtype == np.uint8:  # 8-bit WAV files are usually unsigned
        data = (data.astype(np.float32) - 128) / np.iinfo(np.uint8).max  # adjusting range to [-1, 1]
    
    return fs, data

def write_array_to_wav(file_name: str, audio_data, fs):
    date_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    output_file = f'_output/{date_time}-{file_name}.wav'
    write(output_file, fs, audio_data)
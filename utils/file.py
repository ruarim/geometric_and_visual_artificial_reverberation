from scipy.io.wavfile import write, read, WavFileWarning
from datetime import datetime
from os import path, makedirs
import numpy as np
import warnings
import csv
import json

def read_wav_file(data_dir: str, file_name: str): 
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", WavFileWarning)
        # construct the path to the WAV file.
        wav_fname = path.join(data_dir, file_name)
        # read the WAV file.
        fs, data = read(wav_fname)
    
    # determine the bit depth of the data and normalize it to the range [-1, 1].
    if data.dtype == np.int16:
        data = data.astype(np.float32) / np.iinfo(np.int16).max
    elif data.dtype == np.int32:
        data = data.astype(np.float32) / np.iinfo(np.int32).max
    elif data.dtype == np.uint8:  # 8-bit WAV files are usually unsigned
        data = (data.astype(np.float32) - 128) / np.iinfo(np.uint8).max  # adjusting range to [-1, 1]
    
    return fs, data

def write_array_to_wav(dir: str, file_name: str, audio_data, fs, time_stamp=True):
    # Create the directory if it doesn't exist
    if isinstance(audio_data, list): 
        audio_data = np.array(audio_data)
        
    if not path.exists(dir):
        makedirs(dir)
    
    if time_stamp: date_time = f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}-"
    else: date_time = ''
    output_file = f'{dir}{date_time}{file_name}.wav'
    write(output_file, fs, audio_data)
    
def read_csv(path):
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        # Read the header row
        header = next(reader)
        # Initialize a dictionary to store columns
        columns = {column: [] for column in header}
                
        # Iterate through the rows and populate the columns
        for row in reader:
            for i, column in enumerate(header):
                columns[column].append(row[i])
        
        return columns

def read_json(path):
    with open(path, 'r') as jsonfile:
        data = json.load(jsonfile)
    return data

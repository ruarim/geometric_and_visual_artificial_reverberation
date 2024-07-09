from math import floor

# constants
FS = 44100
SIGNAL_LENGTH = 44100
MAX_DELAY_SECS = 1.0
MAX_DELAY = floor(MAX_DELAY_SECS * FS)
SPEED_OF_SOUND = 343.0

# parameters
WALL_ABSORPTION = 0.25 # extend to be defined for each wall
ROOM_DIMS = [15, 17, 15] # x, y, z - length, width, height
SOURCE_LOC = [4.9, 4.5, 2.5] # place in center for evaluation - same below
MIC_LOC = [4.4, 2.8, 2.7]
CHANNEL_LEVELS = [1.0, 1.0] # left, right - use azimuth instead
DIRECT_PATH=False
ER_ORDER=3

# test signal
TEST_SIGNAL = "unit" # unit, noise, pulse, file
BURST_LENGTH = 0.01
DATA_DIR = "_samples/"
FILE_NAME = "Clap 808 Color 03.wav"

# outputs
OUTPUT_TO_FILE = False
PLOT = True
TIMER = False

CONFIG = {
    "FS": 44100,
    "SIGNAL_LENGTH": 44100,
    "MAX_DELAY_SECS": 1.0,
    "MAX_DELAY": floor(MAX_DELAY_SECS * FS),
    "SPEED_OF_SOUND": 343.0,
    "WALL_ABSORPTION": 0.25, # extend to be defined for each wall
    "ROOM_DIMS": [15, 17, 15], # x, y, z - length, width, height
    "SOURCE_LOC": [4.9, 4.5, 2.5], # place in center for evaluation - same below
    "MIC_LOC": [4.4, 2.8, 2.7],
    "CHANNEL_LEVELS": [1.0, 1.0], # left, right - use azimuth instead
    'DIRECT_PATH': False,
    "ER_ORDER": 1,
    "TEST_SIGNAL": "unit", # unit, noise, pulse, file
    "BURST_LENGTH": 0.01,
    "DATA_DIR": "_samples/",
    "FILE_NAME": "Clap 808 Color 03.wav",
    "OUTPUT_TO_FILE": False,
    "PLOT": True,
    "TIMER": False,
}
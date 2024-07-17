from math import floor
from dataclasses import dataclass

@dataclass
class SimulationConfig:
    FS: int = 44100
    SIGNAL_LENGTH: int = 44100
    MAX_DELAY_SECS: float = 1.0
    MAX_DELAY: int = floor(1.0 * FS)
    SPEED_OF_SOUND: float = 343.0

@dataclass
class RoomConfig:
    WALL_ABSORPTION: list = (0.25, 0.25, 0.25, 0.25, 0.25, 0.25)
    #WALL_ABSORPTION_BANDS - 2D array of absorption at freq bands for each wall - from surface descriptions file
    ROOM_DIMS: list = (5, 7, 5)
    SOURCE_LOC: list = (2.9, 2.5, 2.5)
    MIC_LOC: list = (2.4, 2.8, 2.7)
    CHANNEL_LEVELS: list = (1.0, 1.0)
    DIRECT_PATH: bool = False
    ER_ORDER: int = 2

@dataclass
class TestConfig:
    SIGNAL_TYPE: str = "unit"
    BURST_LENGTH: float = 0.01
    SAMPLES_DIR: str = "_samples/"
    FILE_NAME: str = "Clap 808 Color 03.wav"
    ER_RIR_DIR: str = "_output/early_reflections_rirs"
    LR_RIR_DIR: str = "_output/late_reverberation_rirs"
    FULL_RIR_DIR: str = "_output/full_rirs"

@dataclass
class OutputConfig:
    OUTPUT_TO_FILE: bool = True
    PLOT: bool = True
    TIMER: bool = False
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
    WALL_ABSORPTION: float = 0.25
    ROOM_DIMS: list = (5, 7, 5)
    SOURCE_LOC: list = (2.9, 2.5, 2.5)
    MIC_LOC: list = (4.4, 4.8, 4.7)
    CHANNEL_LEVELS: list = (1.0, 1.0)
    DIRECT_PATH: bool = False
    ER_ORDER: int = 2

@dataclass
class TestSignalConfig:
    TEST_SIGNAL: str = "unit"
    BURST_LENGTH: float = 0.01
    DATA_DIR: str = "_samples/"
    FILE_NAME: str = "Clap 808 Color 03.wav"

@dataclass
class OutputConfig:
    OUTPUT_TO_FILE: bool = False
    PLOT: bool = True
    TIMER: bool = False
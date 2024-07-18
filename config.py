from math import floor
from dataclasses import dataclass, field

@dataclass
class SimulationConfig:
    FS: int = 44100
    SIGNAL_LENGTH: int = 22050
    MAX_DELAY_SECS: float = 1.0
    MAX_DELAY: int = floor(1.0 * FS)
    SPEED_OF_SOUND: float = 343.0

@dataclass
class RoomConfig:
    WALL_ABSORPTION: dict = field(default_factory=lambda: {
        "north": 0.25,
        "south": 0.25,
        "east": 0.25,
        "west": 0.25,
        "floor": 0.25,
        "ceiling": 0.25,
    })
    #WALL_ABSORPTION_BANDS - 2D array of absorption at freq bands for each wall - from surface descriptions file get_absorption_coeffs("material_name") 
    ROOM_DIMS: tuple = (5, 7, 5)
    SOURCE_LOC: tuple = (2.9, 2.5, 2.5)
    MIC_LOC: tuple = (2.4, 2.8, 2.7)
    CHANNEL_LEVELS: tuple = (1.0, 1.0)
    DIRECT_PATH: bool = False
    ER_ORDER: int = 2

@dataclass
class TestConfig:
    SIGNAL_TYPE: str = "unit"
    BURST_LENGTH: float = 0.01
    SAMPLES_DIR: str = "_samples/"
    FILE_NAME: str = "vital_saw.wav"
    ER_RIR_DIR: str = "_output/early_reflections_rirs/" 
    LR_RIR_DIR: str = "_output/late_reverberation_rirs/"
    FULL_RIR_DIR: str = "_output/full_rirs/"

@dataclass
class OutputConfig:
    OUTPUT_TO_FILE: bool = False
    PLOT: bool = True
    TIMER: bool = False
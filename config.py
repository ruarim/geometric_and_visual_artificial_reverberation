from math import floor
from dataclasses import dataclass, field

@dataclass
class SimulationConfig:
    FS: int = 44100
    SIGNAL_LENGTH: int = (FS * 10)
    MAX_DELAY_SECS: float = 1.0
    MAX_DELAY: int = floor(1.0 * FS)
    SPEED_OF_SOUND: float = 343.0

@dataclass
class RoomConfig:
    WALL_ABSORPTION: dict = field(default_factory=lambda: {
        "north": 0.1,
        "south": 0.1,
        "east": 0.1,
        "west": 0.1,
        "floor": 0.1,
        "ceiling": 0.1,
    })
    WALL_MATERIALS: dict = field(default_factory=lambda: {
        "north": "hard_surface",
        "south": "hard_surface",
        "east": "hard_surface",
        "west": "hard_surface",
        "floor": "hard_surface",
        "ceiling": "hard_surface",
    })
    MODEL_PATH: str = ""
    MATERIALS_DIR: str = "_data/vorlander_auralization/materials.json"
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
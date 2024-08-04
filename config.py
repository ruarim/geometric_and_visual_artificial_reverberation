from math import floor
from dataclasses import dataclass, field
from utils.models3D import get_room_dims

@dataclass
class SimulationConfig:
    FS: int = 44100
    SIGNAL_LENGTH: int = (FS * 5)
    MAX_DELAY_SECS: float = 1.0
    MAX_DELAY: int = floor(1.0 * FS)
    SPEED_OF_SOUND: float = 343.0

@dataclass
class RoomConfig:
    WALL_ABSORPTION: dict = field(default_factory=lambda: {
        "north": 0.0306,
        "south": 0.0306,
        "east": 0.0306,
        "west": 0.0306,
        "floor": 0.0306,
        "ceiling": 0.0306,
    })
    WALL_MATERIALS: dict = field(default_factory=lambda: {
        "north": "hard_surface",
        "south": "hard_surface",
        "east": "hard_surface",
        "west": "hard_surface",
        "floor": "linoleum_on_concrete",
        "ceiling": "hard_surface",
    })
    MATERIALS_DIR: str = "_data/vorlander_auralization/materials.json"
    ROOM_DIMS: tuple = field(default_factory=lambda: get_room_dims('_rooms/small_hallway.obj'))
    SOURCE_LOC: tuple = (1.0, 1.5, 1.0)
    MIC_LOC: tuple = (1.9, 1.5, 1.0)
    CHANNEL_LEVELS: tuple = (1.0, 1.0)
    DIRECT_PATH: bool = False
    ER_ORDER: int = 2
    MODEL_PATH: str = '_rooms/small_hallway.obj'

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
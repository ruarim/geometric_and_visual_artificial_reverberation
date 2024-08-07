from math import floor
from dataclasses import dataclass, field
from utils.models3D import get_room_dims

@dataclass
class SimulationConfig:
    FS: int = 44100
    SIGNAL_LENGTH: int = (FS * 3)
    MAX_DELAY_SECS: float = 1.0
    MAX_DELAY: int = floor(1.0 * FS)
    SPEED_OF_SOUND: float = 343.0

@dataclass
class RoomConfig:
    WALL_ABSORPTION: dict = field(default_factory=lambda: { # flat absorption
        "north": 0.0306,
        "south": 0.0306,
        "east": 0.0306,
        "west": 0.0306,
        "floor": 0.0306,
        "ceiling": 0.0306,
    })
    WALL_MATERIALS: dict = field(default_factory=lambda: { # custom materials
        "north": "plasterboard",
        "south": "plasterboard",
        "east": "plasterboard",
        "west": "plasterboard",
        "floor": "linoleum_on_concrete",
        "ceiling": "plasterboard",
    })
    WALL_IMAGE_MATERIALS: dict = field(default_factory=lambda: { # estimated from image
        "north": "/path/",
        "south": "/path/",
        "east": "/path/",
        "west": "/path/",
        "floor": "/path/",
        "ceiling": "/path/",
    })
    MATERIALS_DIR: str = "_data/vorlander_auralization/materials.json"
    ROOM_DIMS: tuple = field(default_factory=lambda: get_room_dims('_rooms/small_hallway.obj'))
    SOURCE_LOC: tuple = (0.5, 1.03,  1.25) # length, width, height
    MIC_LOC: tuple = (2.2, 1.02, 1.35)
    CHANNEL_LEVELS: tuple = (1.0, 1.0)
    DIRECT_PATH: bool = False
    ER_ORDER: int = 2
    MODEL_PATH: str = '_rooms/small_hallway.obj'

@dataclass
class TestConfig:
    SIGNAL_TYPE: str = "unit"
    BURST_LENGTH: float = 0.01
    SAMPLES_DIR: str = "_anechoic_samples/"
    FILE_NAME: str = "Clap 808 Color 03.wav"
    ER_RIR_DIR: str = "_output/early_reflections_rirs/" 
    LR_RIR_DIR: str = "_output/late_reverberation_rirs/"
    FULL_RIR_DIR: str = "_output/full_rirs/"
    REAL_RIR_FILE: str = "small_hallway_rir.wav"

@dataclass
class OutputConfig:
    OUTPUT_TO_FILE: bool = False
    PLOT: bool = True
    TIMER: bool = False
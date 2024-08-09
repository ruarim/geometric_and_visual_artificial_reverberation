from math import floor
from dataclasses import dataclass, field
from utils.models3D import get_room_dims
from utils.material_recognition import image_to_material

MATERIALS_DIR: str = "_data/vorlander_auralization/materials.json"
MANUAL_MATERIALS: bool = False
ROOM_DIR: str = '_rooms'
ROOM_IMAGES_DIR: str = 'small_hallway_images'

@dataclass
class SimulationConfig:
    FS: int = 44100
    SIGNAL_LENGTH: int = (FS * 3)
    MAX_DELAY_SECS: float = 1.0
    MAX_DELAY: int = floor(1.0 * FS)
    SPEED_OF_SOUND: float = 343.0

@dataclass
class RoomConfig:
    WALL_MATERIALS_FLAT: dict = field(default_factory=lambda: { # flat absorption
        "north": 0.0306,
        "south": 0.0306,
        "east": 0.0306,
        "west": 0.0306,
        "floor": 0.0306,
        "ceiling": 0.0306,
    })
    WALL_MATERIALS: dict = field(default_factory=lambda: {
        "north": "wooden_door" if MANUAL_MATERIALS else image_to_material(MATERIALS_DIR, f"{ROOM_DIR}/{ROOM_IMAGES_DIR}/north.PNG"),
        "south": "wooden_door" if MANUAL_MATERIALS else image_to_material(MATERIALS_DIR, f"{ROOM_DIR}/{ROOM_IMAGES_DIR}/south.PNG"),
        "east": "plasterboard" if MANUAL_MATERIALS else image_to_material(MATERIALS_DIR, f"{ROOM_DIR}/{ROOM_IMAGES_DIR}/east.PNG"),
        "west": "plasterboard" if MANUAL_MATERIALS else image_to_material(MATERIALS_DIR, f"{ROOM_DIR}/{ROOM_IMAGES_DIR}/west.png"),
        "floor": "linoleum_on_concrete" if MANUAL_MATERIALS else image_to_material(MATERIALS_DIR, f"{ROOM_DIR}/{ROOM_IMAGES_DIR}/floor.PNG"),
        "ceiling": "plasterboard" if MANUAL_MATERIALS else image_to_material(MATERIALS_DIR, f"{ROOM_DIR}/{ROOM_IMAGES_DIR}/ceiling.PNG"),
    })
    MATERIALS_DIR: str = MATERIALS_DIR
    WALL_MATERIALS_TYPE: str = 'image' # TODO
    ROOM_DIMS: tuple = field(default_factory=lambda: get_room_dims(f'{ROOM_DIR}/small_hallway.obj'))
    SOURCE_LOC: tuple = (0.5, 1.03,  1.25) # length, width, height
    MIC_LOC: tuple = (2.2, 1.02, 1.35)
    CHANNEL_LEVELS: tuple = (1.0, 1.0)
    DIRECT_PATH: bool = False
    ER_ORDER: int = 2
    MODEL_PATH: str = '_rooms/small_hallway.obj'
    SCHRODER_MULTIIPLE = 2

@dataclass
class TestConfig:
    SIGNAL_TYPE: str = "unit"
    BURST_LENGTH: float = 0.01
    SAMPLES_DIR: str = "_anechoic_samples/"
    FILE_NAME: str = "drums.wav"
    ER_RIR_DIR: str = "_output/early_reflections_rirs/" 
    LR_RIR_DIR: str = "_output/late_reverberation_rirs/"
    FULL_RIR_DIR: str = "_output/full_rirs/"
    REAL_RIR_FILE: str = "small_hallway_rir.wav"
    PROCESSED_SAMPLES_DIR: str = '_output/processed_samples/'

@dataclass
class OutputConfig:
    OUTPUT_TO_FILE: bool = False
    PLOT: bool = True
    TIMER: bool = False
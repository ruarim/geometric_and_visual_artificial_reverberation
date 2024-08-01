from utils.models3D import get_room_dims
from utils.plot import plot_room, show_plots
from config import RoomConfig


room_config = RoomConfig()

dims = get_room_dims(room_config.MODEL_PATH)
length, width, height = dims

print(f'Length: {length}')
print(f'Width: {width}')
print(f'Height: {height}')

source = room_config.SOURCE_LOC
mic = room_config.MIC_LOC
plot_room(dims, source, mic)
show_plots()

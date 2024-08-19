import numpy as np

from config import SimulationConfig, RoomConfig, TestConfig, OutputConfig
from utils.signals import signal
from utils.file import write_array_to_wav

from ism_fdn import ISMFDN
from sdn import SDN
from early_reflections.ism import ImageSourceMethod

# config dataclasses
simulation_config = SimulationConfig()
room_config = RoomConfig()
test_config = TestConfig()
output_config = OutputConfig()
    
def rirs_config(fs):
    print(f'Synthesising RIRs, sample rate: {fs}')
    
    unit_impulse, _ = signal(
        'unit', 
        simulation_config.SIGNAL_LENGTH, 
        fs, 
        data_dir=test_config.SAMPLES_DIR, 
        file_name=test_config.FILE_NAME,
    )
    
    fdn_N_delays = 16
    """
    Process RIR:
    (early reflection) ism tapped delay line 
    (late reflections) velvet fdn using all image source delays and random ortogonal martrix, output taken from mixing matrix.
    """
    ism_fdn_all_delays = ISMFDN(
        fs, 
        simulation_config, 
        room_config, 
        fdn_N=-1, 
        processing_type='parallel',
    )
    fdn_ism_N = len(ism_fdn_all_delays.fdn_delay_times)
    ism_fdn_all_delays = ism_fdn_all_delays.process(unit_impulse)
    
    """
    Process RIR:
    (early reflection) ism tapped delay line
    (late reflections) velvet fdn using 16 image source delays and hadamard martrix, output taken from mixing matrix.
    """
    ism_fdn_N_delays = ISMFDN(
        fs, 
        simulation_config, 
        room_config, 
        fdn_N=fdn_N_delays, 
        processing_type='parallel'
    ).process(unit_impulse)

    """
    Process RIR:
    (early and late reflections) Only FDN with standard fdn using 16 image source delays and a hadamard matrx, output taken from delay lines.
    """
    ism_fdn_hadamard = ISMFDN(
        fs, 
        simulation_config,
        room_config, 
        fdn_N=fdn_N_delays, 
        processing_type='fdn_only'
    ).process(unit_impulse)

    """
    Process scattering delay network with fir wall filters.
    """
    sdn = SDN(
        fs, 
        simulation_config, 
        room_config
    ).process(unit_impulse)
    
    """
    Process image source method via pyroomacoustics.
    """
    ism = ImageSourceMethod(
        room_config,
        fs=fs
    ).process(order=200, norm=True)
    
    
    return [
        {
            'name': f"ISMFDN, One-pole, N={fdn_ism_N}",
            'rir': ism_fdn_all_delays[0],
        },
        {
            'name': f"ISMFDN, FIR, N={fdn_ism_N}",
            'rir': ism_fdn_all_delays[1],
        },
        {
            'name': f"ISMFDN, One-pole, N={fdn_N_delays}",
            'rir': ism_fdn_N_delays[0],
        },
        {
            'name': f"ISMFDN, FIR, N={fdn_N_delays}",
            'rir': ism_fdn_N_delays[1],
        },
        {
            'name': f"Hadamard FDN, One-pole, N={fdn_N_delays}",
            'rir': ism_fdn_hadamard,
        },
        {
            'name': "SDN",
            'rir': sdn,
        },
        {
            'name': 'ISM, Order=200',
            'rir': ism,
        },
    ]


# create all rirs
norm = True
output_dir = f"{test_config.FULL_RIR_DIR}"
fs = simulation_config.FS
rirs = rirs_config(fs)

# generate RIR and apply to target audio   
for rir in rirs:
    name = rir['name']
    rir  = rir['rir']
    
    if isinstance(rir, tuple): 
        print('not signal')
        continue
        
    # output rir
    write_array_to_wav(
        output_dir, 
        f"{name}", 
        rir, 
        fs, 
        time_stamp=False
    )
    print(f'Saved {name}')
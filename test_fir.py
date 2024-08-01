from utils.filters import plot_fir
import numpy as np
from utils.signals import signal

fs = 44100

# frequency bands and attenuation values
freqs = np.array([125, 250, 500, 1000, 2000, 4000, 8000])
gains = np.array([0.07, 0.31, 0.49, 0.81, 0.66, 0.54, 0.48])

# get alpha from absorption coeffs
gains = 1 - gains

x, fs = signal('noise', burst_secs=0.5)

plot_fir(x, freqs, gains, fs, db=True)
import numpy as np

def rms_diff(predicted, observed):
    squared_differences = np.square(predicted - observed)
    mean_squared_difference = np.mean(squared_differences)
    rmsd = np.sqrt(mean_squared_difference)
    
    return rmsd
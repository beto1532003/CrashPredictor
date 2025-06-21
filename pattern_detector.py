import numpy as np
from scipy.stats import linregress

def detect_pattern_type(values):
    values = np.array(values)

    x = np.arange(len(values))
    slope, intercept, r_value, _, _ = linregress(x, values)
    if r_value ** 2 > 0.95:
        return "LCG"

    std_dev = np.std(values)
    if 10 < std_dev < 15:
        return "PRNG"

    return "HASH"

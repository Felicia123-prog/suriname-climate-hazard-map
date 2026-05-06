import numpy as np
from scipy.interpolate import Rbf

def rbf_interpolation(lons, lats, values, xi, yi):
    # RBF met multiquadric kernel geeft mooie vloeiende regenvelden
    rbf = Rbf(lons, lats, values, function='multiquadric', smooth=0.1)
    z = rbf(xi, yi)
    return z

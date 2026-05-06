import numpy as np
from pykrige.ok import OrdinaryKriging

def kriging_interpolation(lons, lats, values, xi, yi):
    OK = OrdinaryKriging(
        lons,
        lats,
        values,
        variogram_model="spherical",
        verbose=False,
        enable_plotting=False
    )

    z, ss = OK.execute("grid", xi[0], yi[:, 0])
    return z

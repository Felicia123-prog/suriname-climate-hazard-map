import numpy as np
from scipy.spatial import cKDTree

def idw_interpolation(x, y, z, xi, yi, power=2):
    """Voert IDW-interpolatie uit op punten."""
    coords = np.vstack((x, y)).T
    tree = cKDTree(coords)

    interp_points = np.vstack((xi.flatten(), yi.flatten())).T
    dist, idx = tree.query(interp_points, k=6)

    weights = 1 / (dist ** power + 1e-12)
    z_interp = np.sum(weights * z[idx], axis=1) / np.sum(weights, axis=1)

    return z_interp.reshape(xi.shape)


import math
import numpy as np

#TODO: rename module

def rbf(x, y, lengthscale):
    return np.exp(-np.linalg.norm(x - y)**2.0/(2.0 * lengthscale**2.0))

def paint_heatmap(heatmap, points, lengthscale, radius=None):
    # Outside this radius, the rbf value is so small it doesn't matter.
    radius = math.ceil(4.5 * lengthscale)
    hit = False
    for point in points:
        point_int = np.round(point).astype(np.int)
        for j in range(max(point_int[1] - radius, 0), min(point_int[1] + radius, heatmap.shape[0])):
            for i in range(max(point_int[0] - radius, 0), min(point_int[0] + radius, heatmap.shape[1])):
                hit = True
                coordinate = np.array([i, j], dtype=point.dtype) + 0.5
                heatmap[j, i] = rbf(point, coordinate, lengthscale)
    if hit:
        heatmap /= heatmap.max()


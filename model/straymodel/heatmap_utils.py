import numpy as np

#TODO: rename module

def rbf(x, y, lengthscale):
    return np.exp(-np.linalg.norm(x - y)**2.0/(2.0 * lengthscale**2.0))

def paint_heatmap(heatmap, points, lengthscale):
    hit = False
    radius = int(4.0 * lengthscale)
    for point in points:
        point_int = np.round(point).astype(np.int)
        for j in range(max(point_int[1] - radius, 0), min(point_int[1] + radius, heatmap.shape[0])):
            for i in range(max(point_int[0] - radius, 0), min(point_int[0] + radius, heatmap.shape[1])):
                hit = True
                coordinate = np.array([i, j], dtype=point.dtype)
                heatmap[j, i] = rbf(point, coordinate, lengthscale) + 0.5
    if hit:
        heatmap /= heatmap.max()


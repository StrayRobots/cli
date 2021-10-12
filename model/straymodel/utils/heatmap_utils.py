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
        point_x, point_y = point
        for y in range(heatmap.shape[0]):
            for x in range(heatmap.shape[1]):
                #TODO: maybe somehting accordong to the bbox dimensions vs circle
                if np.sqrt(np.linalg.norm(y-point_y)**2+np.linalg.norm(x-point_x)**2) <= radius:
                    hit = True
                    coordinate = np.array([x, y], dtype=point.dtype)
                    heatmap[y, x] = rbf(point, coordinate, lengthscale) + 0.5
    if hit:
        heatmap /= np.sum(heatmap)


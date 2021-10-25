import torch
from straymodel.utils.visualization_utils import save_example
import os
from straymodel.train.objectron import objectron_features as features
import numpy as np
from straymodel.utils.heatmap_utils import paint_heatmap
import cv2
from straylib.camera import get_scaled_camera_matrix

I = np.eye(3)
WIDTH = 480
OUT_WIDTH = 60
HEIGHT = 640
OUT_HEIGHT = 80
NUM_CHANNELS = 3

def get_blank_maps():
    x_range = np.arange(OUT_WIDTH)
    y_range = np.arange(OUT_HEIGHT)
    corner_map_x = np.tile(x_range, (OUT_HEIGHT, 1))
    corner_map_y = np.tile(y_range, (OUT_WIDTH, 1)).T
    corner_map_stack = np.stack([corner_map_x, corner_map_y])
    blank_corner_map = np.tile(corner_map_stack, (8, 1, 1))
    blank_heatmap = np.zeros((1, OUT_HEIGHT, OUT_WIDTH), dtype=np.float32)
    return blank_corner_map, blank_heatmap

def get_image(data):
    data['image'] = cv2.imdecode(data['image/encoded'], -1)
    data['image'] = data['image'].astype(np.float32) / 255.0
    return np.transpose(data['image'], [2, 0, 1])

def get_image_filename(data):
    return data[features.FEATURE_NAMES['IMAGE_FILENAME']].numpy().decode("utf-8")

def get_image_id(data):
    return data[features.FEATURE_NAMES['IMAGE_ID']].numpy()[0]

def get_heatmap(data, blank_heatmap):
    translation = data['object/translation']
    intrinsics = data['camera/intrinsics'].reshape((3, 3))
    scale = data['object/scale']
    points_2d = data['point_2d']

    scaled_intrinsics = get_scaled_camera_matrix(intrinsics, 0.125, 0.125)
    heatmap = np.copy(blank_heatmap)
    diagonal_fraction = np.linalg.norm(scale, 2) * 0.125 # 1/8.
    R, _ = cv2.Rodrigues(I)
    top, _ = cv2.projectPoints((translation - I[1] * diagonal_fraction)[None], R, np.zeros(3), scaled_intrinsics, np.zeros(4))
    top_point = top[:, 0, :][0]
    bottom, _ = cv2.projectPoints((translation + I[1] * diagonal_fraction)[None], R, np.zeros(3), scaled_intrinsics, np.zeros(4))
    bottom_point = bottom[:, 0, :][0]
    size = np.linalg.norm(top_point - bottom_point) / 4.0
    lengthscale = np.sqrt(size**2/20.0)
    center_point = points_2d[:3][:2]*np.array([OUT_WIDTH, OUT_HEIGHT])
    paint_heatmap(heatmap[0], [center_point], lengthscale)
    heatmap_max = heatmap.max()
    return heatmap

def get_corner_maps(data, blank_corner_map):
    corner_map = np.copy(blank_corner_map)
    points_2d = data['point_2d']
    projected = points_2d[3:].reshape((8,3))[:,:2]*np.array([OUT_WIDTH, OUT_HEIGHT])
    for j, point in enumerate(projected):
        corner_map[j*2] = point[0] - corner_map[j*2]
        corner_map[j*2 +1] = point[1] - corner_map[j*2+1]
    return corner_map

def save_objectron_sample(folder, images, heatmaps, corner_maps, cameras, sizes):
    for j, (image, heatmap, corner_map, camera, size) in enumerate(zip(images, heatmaps, corner_maps, cameras, sizes)):
        save_example(image, heatmap, corner_map, camera, size, folder, j)

def unpack_record(blank_corner_map, blank_heatmap):
    def inner(data):
        instances = data['instance_num']
        if not instances[0] == 1:
            return False, None
        else:
            images = torch.from_numpy(get_image(data)).float()
            heatmaps = torch.from_numpy(get_heatmap(data, blank_heatmap)).float()
            corner_maps = torch.from_numpy(get_corner_maps(data, blank_corner_map)).float()
            intrinsics = data['camera/intrinsics'].reshape((3, 3))
            sizes = data['object/scale']
            return True, (images, heatmaps, corner_maps, intrinsics, sizes)
    return inner


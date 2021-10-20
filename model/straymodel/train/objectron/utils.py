import torch
from straymodel.utils.visualization_utils import save_example
import os
from straymodel.train.objectron import objectron_features as features
import tensorflow as tf
import numpy as np
from straymodel.utils.heatmap_utils import paint_heatmap
import cv2
from straylib.camera import get_scaled_camera_matrix
import tensorflow as tf


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

def get_tfdata_field(data, feature_name):
    return data[features.FEATURE_NAMES[feature_name]].values.numpy()

def get_tfdata_image(data):
    data['image'] = tf.image.decode_png(data[features.FEATURE_NAMES['IMAGE_ENCODED']], channels=NUM_CHANNELS)
    data['image'].set_shape([HEIGHT, WIDTH, NUM_CHANNELS])
    data['image'] = tf.cast(data['image'], tf.float32) * (2. / 255.) - 1.0
    image = tf.cast((data['image'] + 1.0) / 2.0 * 255, tf.uint8).numpy()
    image = np.moveaxis(image, -1, 0)
    return image[np.newaxis, ...]

def get_image_filename(data):
    return data[features.FEATURE_NAMES['IMAGE_FILENAME']].numpy().decode("utf-8")

def get_image_id(data):
    return data[features.FEATURE_NAMES['IMAGE_ID']].numpy()[0]

def get_heatmap(data, blank_heatmap):
    translation = get_tfdata_field(data, 'OBJECT_TRANSLATION')
    intrinsics = get_tfdata_field(data, 'INTRINSIC_MATRIX').reshape((3,3))
    scale = get_tfdata_field(data, 'OBJECT_SCALE')
    points_2d = get_tfdata_field(data, 'POINT_2D')

    scaled_intrinsics = get_scaled_camera_matrix(intrinsics, 0.125, 0.125)
    heatmap = np.copy(blank_heatmap)
    diagonal_fraction = np.linalg.norm(scale, 2) * 0.125 # 1/8.
    R, _ = cv2.Rodrigues(I)
    top, _ = cv2.projectPoints((translation - I[1] * diagonal_fraction)[None], R, np.zeros(3), scaled_intrinsics, np.zeros(4))
    top_point = top[:, 0, :][0]
    bottom, _ = cv2.projectPoints((translation + I[1] * diagonal_fraction)[None], R, np.zeros(3), scaled_intrinsics, np.zeros(4))
    bottom_point = bottom[:, 0, :][0]
    size = np.linalg.norm(top_point - bottom_point)
    lengthscale = np.sqrt(size**2/20.0)
    center_point = points_2d[:3][:2]*np.array([OUT_WIDTH, OUT_HEIGHT])
    paint_heatmap(heatmap[0], [center_point], lengthscale)
    return heatmap[np.newaxis, ...]

def get_corner_maps(data, blank_corner_map):
    corner_map = np.copy(blank_corner_map)
    points_2d = get_tfdata_field(data, 'POINT_2D')
    projected = points_2d[3:].reshape((8,3))[:,:2]*np.array([OUT_WIDTH, OUT_HEIGHT])
    for j, point in enumerate(projected):
        corner_map[j*2] = point[0] - corner_map[j*2]
        corner_map[j*2 +1] = point[1] - corner_map[j*2+1]
    return corner_map[np.newaxis, ...]

def save_objectron_sample(folder, images, heatmaps, corner_maps, cameras, sizes):
    for j, (image, heatmap, corner_map, camera, size) in enumerate(zip(images, heatmaps, corner_maps, cameras, sizes)):
        save_example(image, heatmap, corner_map, camera, size, folder, j)

def get_batch_from_record(tf_batch, blank_heatmap, blank_corner_map):
    valid_batch = False
    for raw_record in tf_batch:
        data = tf.io.parse_single_example(raw_record, features = features.FEATURE_MAP)
        instances = data[features.FEATURE_NAMES['INSTANCE_NUM']].numpy()
        if not instances[0] == 1:
            continue
        elif not valid_batch:
            images = torch.from_numpy(get_tfdata_image(data)).float()
            heatmaps = torch.from_numpy(get_heatmap(data, blank_heatmap)).float()
            corner_maps = torch.from_numpy(get_corner_maps(data, blank_corner_map)).float()
            intrinsics = get_tfdata_field(data, 'INTRINSIC_MATRIX').reshape((1,3,3))
            sizes = get_tfdata_field(data, 'OBJECT_SCALE')
            valid_batch = True
        else:
            images = torch.cat((images, torch.from_numpy(get_tfdata_image(data)).float()))
            heatmaps = torch.cat((heatmaps, torch.from_numpy(get_heatmap(data, blank_heatmap)).float()))
            corner_maps = torch.cat((corner_maps, torch.from_numpy(get_corner_maps(data, blank_corner_map)).float()))
            intrinsics = np.vstack((intrinsics, get_tfdata_field(data, 'INTRINSIC_MATRIX').reshape((1,3,3))))
            sizes = np.vstack((sizes, get_tfdata_field(data, 'OBJECT_SCALE')))
    
    if valid_batch:
        return valid_batch, (images, heatmaps, corner_maps, intrinsics, sizes)
    else:
        return valid_batch, None

import os
import numpy as np
import pandas as pd
import torch
import cv2
from straylib.scene import Scene
from straylib.camera import Camera
from straylib.export import validate_segmentations
from scipy.spatial.transform import Rotation as R
from straymodel.heatmap_utils import paint_heatmap
from torch.utils.data import Dataset, ConcatDataset

def transform(T, vectors):
    return (T[:3, :3] @ vectors[:, :, None])[:, :, 0] + T[:3, 3]

def get_instance_pose(bbox, image_idx, scene):
    '''
    Returns the pose of the instance relative to the camera as a list [pos, rot(quaternion)]
    '''
    T_WC = scene.poses[image_idx]
    T_CW = np.linalg.inv(T_WC)

    T_WB = np.eye(4)
    T_WB[:3, :3] = bbox.orientation.as_matrix()
    T_WB[:3, 3] = bbox.position

    T_CB = T_CW @ T_WB

    return T_CB

def _to_transform(translation_rotation):
    T = np.eye(4)
    T[:3, 3] = translation_rotation[:3]
    T[:3, :3] = R.from_quat(translation_rotation[-4:]).as_matrix()
    return T

class Stray3DBoundingBoxScene(Dataset):
    def __init__(self, path, image_size=(640, 480), out_size=(60, 80)):
        self.scene_path = path
        self.scene = Scene(path)
        self.image_width = image_size[0]
        self.image_height = image_size[1]
        self.out_width = out_size[0]
        self.out_height = out_size[1]
        self.num_instances = len(self.scene.bounding_boxes)
        validate_segmentations(self.scene)
        self.color_images = self.scene.get_image_filepaths()
        self.camera = self.scene.camera().scale((self.out_width, self.out_height))
        self.indices = np.zeros((self.out_height, self.out_width, 2))
        for i in range(self.out_height):
            for j in range(self.out_width):
                self.indices[i, j] = np.array([j, i])
        self.lengthscale = self.out_width / 64.0
        self.radius = 4.0 * self.lengthscale
        self.max_points = 5

    def __len__(self):
        return len(self.scene)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        image = cv2.imread(self.color_images[idx])
        image = cv2.resize(image, (self.image_width, self.image_height))
        image = np.moveaxis(image, -1, 0) / 255.0
        image = torch.from_numpy(image).float()

        center_map = np.zeros((1, self.out_height, self.out_width), dtype=np.float32)
        corner_map = np.zeros((16, self.out_height, self.out_width), dtype=np.float32)

        T_CW = self.scene.poses[idx]

        # Only single instances supported for now.
        assert len(self.scene.bounding_boxes) == 1
        #TODO: handle case where center is not in frame.

        for i, bounding_box in enumerate(self.scene.bounding_boxes):
            center_point = self.camera.project(bounding_box.position[None], T_CW)
            paint_heatmap(center_map[0], center_point, self.lengthscale)

            c_W = self.scene.bounding_boxes[0].position
            c_C = transform(T_CW, c_W[None])

            # Corner map.
            vertices = bounding_box.vertices()
            projected = self.camera.project(vertices, T_CW)
            for j, point in enumerate(projected):
                where_support = center_map[0] > 0.0
                #TODO: blend corners in proportion to the support in case the centers overlap.
                corner_map[j*2:j*2+2, where_support] = (point - center_point[0])[:, None]
        return image, center_map, corner_map, torch.from_numpy(self.camera.camera_matrix), torch.from_numpy(c_C[0])

class Stray3DBoundingBoxDetectionDataset(ConcatDataset):
    def __init__(self, scene_paths, *args, **kwargs):
        scenes = []
        for scene_path in scene_paths:
            scenes.append(Stray3DBoundingBoxScene(scene_path, *args, **kwargs))
        super().__init__(scenes)


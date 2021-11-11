import os
import numpy as np
import pandas as pd
import torch
import cv2
from straylib.scene import Scene
from straylib.camera import Camera
from scipy.spatial.transform import Rotation as R
from straymodel.utils.heatmap_utils import paint_heatmap
from torch.utils.data import Dataset, ConcatDataset
I = np.eye(3)

def transform(T, vectors):
    return (T[:3, :3] @ vectors[:, :, None])[:, :, 0] + T[:3, 3]
class Stray3DBoundingBoxScene(Dataset):
    def __init__(self, path, image_size=(640, 480), out_size=(80, 60), inference=False):
        self.inference = inference
        self.scene_path = path
        self.scene = Scene(path)
        self.image_width = image_size[0]
        self.image_height = image_size[1]
        self.out_width = out_size[0]
        self.out_height = out_size[1]
        self.num_instances = len(self.scene.bounding_boxes)

        self.color_images = self.scene.get_image_filepaths()
        self.camera = self.scene.camera()
        self.map_camera = self.scene.camera().scale((self.out_width, self.out_height))
        self.indices = np.zeros((self.out_height, self.out_width, 2))
        for i in range(self.out_height):
            for j in range(self.out_width):
                self.indices[i, j] = np.array([j, i])

        self._create_blank_maps()

    def _create_blank_maps(self):
        x_range = np.arange(self.out_width)
        y_range = np.arange(self.out_height)
        corner_map_x = np.tile(x_range, (self.out_height, 1))
        corner_map_y = np.tile(y_range, (self.out_width, 1)).T
        corner_map_stack = np.stack([corner_map_x, corner_map_y])
        self.blank_corner_map = np.tile(corner_map_stack, (8, 1, 1))
        self.blank_heatmap = np.zeros((1, self.out_height, self.out_width), dtype=np.float32)

    def _get_numpy_image(self, idx):
        image = cv2.imread(self.color_images[idx])
        image = cv2.resize(image, (self.image_width, self.image_height))
        image = np.moveaxis(image, -1, 0) / 255.0
        return image


    def __len__(self):
        return len(self.scene)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()



        heatmap = np.copy(self.blank_heatmap)
        corner_map = np.copy(self.blank_corner_map)
        np_image = self._get_numpy_image(idx)

        if self.inference:
            T_CW = np.eye(4)
            size = np.ones(3)
        else:
            T_CW = np.linalg.inv(self.scene.poses[idx])

            for i, bounding_box in enumerate(self.scene.bounding_boxes):
                #TODO: handle cases with multiple boxes
                if i > 0:
                    break
                center_C = transform(T_CW, bounding_box.position[None])[0]
                center_point = self.map_camera.project(center_C)
                # Let's set the heatmap radius to 1/4 of the bounding box's diameter.
                diagonal_fraction = np.linalg.norm(bounding_box.dimensions, 2) * 0.125 # 1/8.
                # Compute the size of the center ball in pixels.
                top_point = self.map_camera.project((center_C - I[1] * diagonal_fraction)[None])[0]
                bottom_point = self.map_camera.project((center_C + I[1] * diagonal_fraction)[None])[0]
                size = np.linalg.norm(top_point - bottom_point)
                lengthscale = np.sqrt(size**2/20.0)

                paint_heatmap(heatmap[0], center_point, lengthscale)
                heatmap[0] /= heatmap.sum()

                # Corner map.
                vertices = bounding_box.vertices()
                projected = self.map_camera.project(vertices, T_CW)
                for j, point in enumerate(projected):
                    #TODO: blend corners in proportion to the support in case the centers overlap.
                    corner_map[j*2] = point[0] - corner_map[j*2]
                    corner_map[j*2 +1] = point[1] - corner_map[j*2+1]
                size = bounding_box.dimensions

        return torch.from_numpy(np_image).float(), heatmap, corner_map, torch.from_numpy(self.map_camera.camera_matrix), torch.from_numpy(size)

class Stray3DBoundingBoxDetectionDataset(ConcatDataset):
    def __init__(self, scene_paths, *args, **kwargs):
        scenes = []
        for scene_path in scene_paths:
            scenes.append(Stray3DBoundingBoxScene(scene_path, *args, **kwargs))
        super().__init__(scenes)


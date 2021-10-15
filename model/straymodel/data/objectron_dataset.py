import os
import numpy as np
import pandas as pd
import torch
import cv2
from straylib.scene import Scene
from straylib.camera import Camera, get_scaled_camera_matrix
from scipy.spatial.transform import Rotation as R
from straymodel.utils.heatmap_utils import paint_heatmap
from torch.utils.data import Dataset, ConcatDataset
I = np.eye(3)

def transform(T, vectors):
    return (T[:3, :3] @ vectors[:, :, None])[:, :, 0] + T[:3, 3]
    
class ObjectronDataset(Dataset):
    def __init__(self, path, image_size=(480, 640), out_size=(60, 80)):
        self.scene_path = path

        self.image_width = image_size[0]
        self.image_height = image_size[1]
        self.out_width = out_size[0]
        self.out_height = out_size[1]

        self.indices = np.zeros((self.out_height, self.out_width, 2))
        for i in range(self.out_height):
            for j in range(self.out_width):
                self.indices[i, j] = np.array([j, i])

        self.index_file_map = dict()

        file_lengths = []
        dir_names = ["points_2d", "color", "centers"]
        file_lengths.append(len(os.listdir(os.path.join(self.scene_path, "points_2d"))))
        file_lengths.append(len(os.listdir(os.path.join(self.scene_path, "color"))))
        file_lengths.append(len(os.listdir(os.path.join(self.scene_path, "centers"))))
        min_idx = np.argmin(file_lengths)
        dir_name = dir_names[min_idx]

        for i, file in enumerate(sorted(os.listdir(os.path.join(self.scene_path, dir_name)))):
            if not file[0] == ".":
                file_idx = file.split(".")[0]
                self.index_file_map[i] = file_idx

        self.scale = np.loadtxt(os.path.join(self.scene_path, "scale.txt"))

        scaled_camera_matrix = get_scaled_camera_matrix(np.loadtxt(os.path.join(self.scene_path, "intrinsics.txt")), self.out_width/self.image_width, self.out_height/self.image_height)
        self.camera = Camera((self.out_width, self.out_height), scaled_camera_matrix, np.zeros(4))


        self._create_blank_maps()

    def _create_blank_maps(self):
        x_range = np.arange(self.out_width)
        y_range = np.arange(self.out_height)
        corner_map_x = np.tile(x_range, (self.out_height, 1))
        corner_map_y = np.tile(y_range, (self.out_width, 1)).T
        corner_map_stack = np.stack([corner_map_x, corner_map_y])
        self.blank_corner_map = np.tile(corner_map_stack, (8, 1, 1))
        self.blank_heatmap = np.zeros((1, self.out_height, self.out_width), dtype=np.float32)

    def __len__(self):
        return len(self.index_file_map)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        idx = self.index_file_map[idx]

        center_C = np.loadtxt(os.path.join(self.scene_path, "centers", f"{idx}.txt"))
        points_2d = np.loadtxt(os.path.join(self.scene_path, "points_2d", f"{idx}.txt"))
        image = cv2.imread(os.path.join(self.scene_path, "color", f"{idx}.png"))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (self.image_width, self.image_height))
        image = np.moveaxis(image, -1, 0) / 255.0

        center_point = points_2d[:3][:2]*np.array([self.out_width, self.out_height])
        projected = points_2d[3:].reshape((8,3))[:,:2]*np.array([self.out_width, self.out_height])
        


        # Let's set the heatmap radius to 1/4 of the bounding box's diameter.
        diagonal_fraction = np.linalg.norm(self.scale, 2) * 0.125 # 1/8.
        # Compute the size of the center ball in pixels.
        top_point = self.camera.project((center_C - I[1] * diagonal_fraction)[None])[0]
        bottom_point = self.camera.project((center_C + I[1] * diagonal_fraction)[None])[0]
        size = np.linalg.norm(top_point - bottom_point)
        lengthscale = np.sqrt(size**2/20.0)

        heatmap = np.copy(self.blank_heatmap)
        paint_heatmap(heatmap[0], [center_point], lengthscale)
        
        # Corner map.

        corner_map = np.copy(self.blank_corner_map)
        for j, point in enumerate(projected):
            #TODO: blend corners in proportion to the support in case the centers overlap.
            corner_map[j*2] = point[0] - corner_map[j*2]
            corner_map[j*2 +1] = point[1] - corner_map[j*2+1]

        return torch.from_numpy(image).float(), heatmap, corner_map, torch.from_numpy(self.camera.camera_matrix), torch.from_numpy(center_C), torch.from_numpy(self.scale)



class ConcatObjectronDataset(ConcatDataset):
    def __init__(self, scene_paths, *args, **kwargs):
        scenes = []
        for scene_path in scene_paths:
            scenes.append(ObjectronDataset(scene_path, *args, **kwargs))
        super().__init__(scenes)
from torch.utils.data import Dataset
import pandas as pd
import os
from straylib.scene import Scene
import numpy as np
from straylib.export import validate_segmentations
from scipy.spatial.transform import Rotation as R
import torch
import cv2


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
    position = T_CB[:3, 3]
    rotation = R.from_matrix(T_CB[:3, :3]).as_quat()

    return list(position) + list(rotation)


class Stray3DSceneDataset(Dataset):
    def __init__(self, scene_paths, width=100, height=100):
        self.scene_paths = scene_paths
        self.width = width
        self.height = height
        self._process_scenes()

    def _process_scenes(self):
        self.data = pd.DataFrame()
        for scene_path in self.scene_paths:
            scene = Scene(scene_path)
            validate_segmentations(scene)
            for i in range(len(scene)):
                data_row = dict()
                data_row["color_path"] = os.path.join(scene_path, "color", f"{i:06}.jpg")
                data_row["num_instances"] = len(scene.bounding_boxes)
                for j, bbox in enumerate(scene.bounding_boxes):
                    data_row[f"instance_{j}_pose"] = get_instance_pose(bbox, i, scene)
                self.data = self.data.append(data_row, ignore_index=True)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        row = self.data.iloc[idx]

        image = cv2.imread(row["color_path"])
        image = cv2.resize(image, (self.width, self.height))
        image = np.moveaxis(image, -1, 0)/255
        image = torch.from_numpy(image).float()


        num_instances = int(row["num_instances"])
        poses = [row[f"instance_{i}_pose"] for i in range(num_instances)]
        poses = torch.as_tensor(poses).float()

        return image, poses #TODO: currently dataloading assumes the same amount of instances, need to add padding in collate
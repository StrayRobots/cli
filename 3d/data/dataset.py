from torch.utils.data import Dataset
import pandas as pd
import os
from straylib.scene import Scene
import numpy as np
from straylib.export import validate_segmentations
from scipy.spatial.transform import Rotation as R
import torch
import pycocotools.mask as mask_util
import pickle
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
    def __init__(self, scene_paths, width=1920, height=1440):
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
                    data_row[f"instance_{j}_segmentation_path"]= os.path.join(scene_path, "segmentation", f"instance_{j}", f"{i:06}.pickle")
                    data_row[f"instance_{j}_pose"] = get_instance_pose(bbox, i, scene)
                    data_row[f"instance_{j}_category"] = bbox.instance_id
                self.data = self.data.append(data_row, ignore_index=True)

    def __len__(self):
        print("dataset len", len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        row = self.data.iloc[idx]

        image = cv2.imread(row["color_path"])
        image = cv2.resize(image, (self.width, self.height))
        image = np.moveaxis(image, -1, 0)/255
        image = torch.from_numpy(image).float()
        annotations = []
        for i in range(int(row["num_instances"])):
            annotation = dict()
            with open(row[f"instance_{i}_segmentation_path"], 'rb') as handle:
                mask = pickle.load(handle)
            mask = mask_util.decode(mask)
            annotation["mask"] = torch.from_numpy(mask).float()
            annotation["pose"] = torch.tensor(row[f"instance_{i}_pose"]).float()
            annotation["category"] = torch.tensor(row[f"instance_{i}_category"]).float()

            annotations.append(annotation)

        sample = {'image': image, 'annotations': annotations}

        return sample
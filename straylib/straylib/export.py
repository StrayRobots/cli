import os
import numpy as np
from detectron2 import structures
from straylib import Scene, linalg

def compute_bounding_box(camera, T_WC, object_mesh):
    T_CW = np.linalg.inv(T_WC)
    vertices = object_mesh.vertices
    ones = np.ones((vertices.shape[0], 1))
    image_points = camera.project(vertices, T_CW)
    upper_left = image_points.min(axis=0)
    lower_right = image_points.max(axis=0)
    return [upper_left.tolist(), lower_right.tolist()]

def detectron2_dataset_function(scenes_folder):
    scenes = os.listdir(scenes_folder)
    scenes.sort()
    examples = []
    for scene_dir in scenes:
        scene_path = os.path.join(scenes_folder, scene_dir)
        if scene_dir[0] == '.' or not os.path.isdir(scene_path):
            continue
        scene = Scene(scene_path)
        width, height = scene.image_size()
        images = scene.image_filepaths()
        bounding_boxes = scene.bounding_boxes
        camera = scene.camera()
        objects = scene.objects()
        image_id = 0
        for image_path, T_WC in zip(images, scene.poses):
            annotations = []
            for obj, bbox in zip(objects, bounding_boxes):
                annotations.append({
                    'category_id': bbox.instance_id,
                    'bbox': compute_bounding_box(camera, T_WC, obj),
                    'bbox_mode': structures.BoxMode.XYXY_ABS.value
                })
            examples.append({
                'file_name': image_path,
                'image_id': image_id,
                'height': height,
                'width': width,
                'annotations': annotations
            })
            image_id += 1
    return examples


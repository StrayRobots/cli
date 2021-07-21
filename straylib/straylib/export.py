import os
import numpy as np
from detectron2 import structures
from straylib import Scene, linalg
import cv2

def compute_image_bbox(camera, T_WC, object_mesh):
    T_CW = np.linalg.inv(T_WC)
    vertices = object_mesh.vertices
    image_points = camera.project(vertices, T_CW)
    upper_left = image_points.min(axis=0)
    lower_right = image_points.max(axis=0)
    return upper_left.tolist() + lower_right.tolist()

def compute_image_keypoints_and_bbox(camera, T_WC, keypoints):
    T_CW = np.linalg.inv(T_WC)
    image_points = camera.project(keypoints, T_CW)
    upper_left = image_points.min(axis=0).astype(int)
    if keypoints.shape[0] == 1:
        lower_right = image_points.max(axis=0).astype(int) + 1
    else:
        lower_right = image_points.max(axis=0).astype(int)

    bbox = upper_left.tolist() + lower_right.tolist()
    flat_keypoints = np.array([[int(kp[0]), int(kp[1]), 2] for kp in image_points]).flatten().tolist()
    return flat_keypoints, bbox



def get_scene_dataset_metadata(scene_paths):
    num_keypoint_categories = 0
    num_bbox_categories = 0
    for scene_path in scene_paths:
        scene = Scene(scene_path)
        num_bbox_categories = max(num_bbox_categories, scene.num_bbox_categories)
        num_keypoint_categories = max(num_keypoint_categories, scene.num_keypoint_categories)
    return {
        'num_keypoint_categories': num_keypoint_categories,
        'num_bbox_categories': num_bbox_categories
    }

def get_detectron2_bbox_dataset_function(scene_paths):
    def inner():
        examples = []
        for scene_path in scene_paths:
            scene = Scene(scene_path)
            width, height = scene.image_size()
            images = scene.image_filepaths()
            bounding_boxes = scene.keypoints
            camera = scene.camera()
            objects = scene.objects()
            image_id = 0
            for image_path, T_WC in zip(images, scene.poses):
                annotations = []
                for obj, bbox in zip(objects, bounding_boxes):
                    annotations.append({
                        'category_id': bbox.instance_id,
                        'bbox': compute_image_bbox(camera, T_WC, obj),
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
    return inner

def get_detectron2_keypoints_dataset_function(scene_paths):
    def inner():
        examples = []
        for scene_path in scene_paths:
            scene = Scene(scene_path)
            width, height = scene.image_size()
            images = scene.image_filepaths()
            keypoints = scene.keypoints
            camera = scene.camera()
            image_id = 0
            for image_path, T_WC in zip(images, scene.poses):
                annotations = []
                keypoint_positions =  np.array([kp.position for kp in keypoints])
                image_keypoints, bbox = compute_image_keypoints_and_bbox(camera, T_WC, keypoint_positions)
                annotations.append({
                    'category_id': 0,
                    'bbox': bbox,
                    'bbox_mode': structures.BoxMode.XYXY_ABS.value,
                    'keypoints': image_keypoints
                })
                '''
                img = cv2.imread(image_path)
                cv2.circle(img, (int(image_keypoints[0]), int(image_keypoints[1])), 5, (0, 0, 255), -1)
                cv2.circle(img, (int(image_keypoints[3]), int(image_keypoints[4])), 5, (0, 0, 255), -1)
                cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 3)
                cv2.imshow("dataload",img)
                cv2.waitKey(100)
                '''
                examples.append({
                    'file_name': image_path,
                    'image_id': image_id,
                    'height': height,
                    'width': width,
                    'annotations': annotations
                })
                image_id += 1
        return examples
    return inner


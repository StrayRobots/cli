import numpy as np
from detectron2 import structures
from straylib import Scene
import cv2

def compute_image_bbox(camera, T_WC, object_mesh):
    T_CW = np.linalg.inv(T_WC)
    vertices = object_mesh.vertices
    image_points = camera.project(vertices, T_CW)
    upper_left = image_points.min(axis=0)
    lower_right = image_points.max(axis=0)
    return upper_left.tolist() + lower_right.tolist()


def compute_instance_keypoints(camera, T_WC, instance, instance_keypoints, max_num_keypoints):
    T_CW = np.linalg.inv(T_WC)
    world_keypoints = [instance.position + instance.orientation.as_matrix()@np.multiply(np.array(kp),instance.dimensions/2) for kp in instance_keypoints]
    image_keypoints = camera.project(np.array(world_keypoints), T_CW)
    flat_keypoints = []
    for image_point in image_keypoints:
        flat_keypoints.append(image_point[0])
        flat_keypoints.append(image_point[1])
        flat_keypoints.append(2)
    while len(flat_keypoints) < max_num_keypoints:
        flat_keypoints += [0, 0, 0]

    return flat_keypoints
    


def get_scene_dataset_metadata(scene_paths):
    instance_categories = []
    max_num_keypoints = 0
    for scene_path in scene_paths:
        scene = Scene(scene_path)
        metadata = scene.metadata
        for bbox_id in scene.bbox_categories:
            if not bbox_id in instance_categories:
                instance_categories.append(bbox_id)
            if metadata is not None:
                bbox_metadata_instance = [instance for instance in metadata["instances"] if instance["instance_id"] == bbox_id]
                if len(bbox_metadata_instance) > 0:
                    max_num_keypoints = max(max_num_keypoints, len(bbox_metadata_instance[0]["keypoints"]))

    instance_category_mapping = {}
    for i, instance_id in enumerate(instance_categories):
        instance_category_mapping[f"instance_{instance_id}"] = i

    return {
        'max_num_keypoints': max_num_keypoints,
        'instance_category_mapping': instance_category_mapping
    }

def get_detectron2_dataset_function(scene_paths, dataset_metadata):
    def inner():
        examples = []
        for scene_path in scene_paths:
            scene = Scene(scene_path)
            width, height = scene.image_size()
            images = scene.image_filepaths()
            bounding_boxes = scene.bounding_boxes
            metadata = scene.metadata
            camera = scene.camera()
            objects = scene.objects()
            image_id = 0
            max_num_keypoints = dataset_metadata["max_num_keypoints"]
            for image_path, T_WC in zip(images, scene.poses):
                annotations = []
                for obj, bbox in zip(objects, bounding_boxes):
                    annotation = {
                        'category_id': dataset_metadata['instance_category_mapping'][f"instance_{bbox.instance_id}"],
                        'bbox': compute_image_bbox(camera, T_WC, obj),
                        'bbox_mode': structures.BoxMode.XYXY_ABS.value
                    }
                    if metadata is not None:
                        bbox_metadata_instance = [instance for instance in metadata["instances"] if instance["instance_id"] == bbox.instance_id]
                        if len(bbox_metadata_instance) > 0 and len(bbox_metadata_instance[0]["keypoints"]) > 0:
                            image_keypoints = compute_instance_keypoints(camera, T_WC, bbox, bbox_metadata_instance[0]["keypoints"], max_num_keypoints)
                            annotation["keypoints"] = image_keypoints
                        else:
                            annotation["keypoints"] = [0 for _ in range(max_num_keypoints*3)]
                    annotations.append(annotation)

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


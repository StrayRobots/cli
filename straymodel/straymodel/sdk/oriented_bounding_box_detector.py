from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
import os
import math
import numpy as np
import cv2
from skspatial.objects import Plane, Line

def load_config(model_path):
    config = get_cfg()
    if os.path.isfile(os.path.join(model_path, "config.yaml")):
        config.merge_from_file(os.path.join(model_path, "config.yaml"))
    
    config.MODEL.WEIGHTS = os.path.join(model_path, "output", "model_final.pth")
    config.MODEL.DEVICE = 'cpu'
    return config


class OrientedBoundingBoxDetector(object):
    def __init__(self, *args, **kwargs):
        self.cfg = kwargs.get('cfg', {})
        self.predictor = DefaultPredictor(self.cfg)

    @staticmethod
    def from_directory(model_path):
        cfg = load_config(model_path)
        return OrientedBoundingBoxDetector(cfg=cfg)

    @staticmethod
    def from_cfg(cfg):
        return OrientedBoundingBoxDetector(cfg=cfg)

    @staticmethod
    def get_ray(width, height, x, y, fx, fy):
        aspect_ratio = width / height
        fovx = 2*math.atan(width/(2*fx))
        fovy= 2*math.atan(height/(2*fy))
        pX = (2.0 * ((x + 0.5) / width) - 1.0) * math.tan(fovx / 2.0) * aspect_ratio
        pY = (1.0 - 2.0 * ((y + 0.5) / height)) * math.tan(fovy / 2.0)
        vector = np.array([pX, -pY, 1])
        return vector / np.linalg.norm(vector)

    @staticmethod
    def get_point_3d_from_depth(instance, depth, image_width, image_height, depth_scale, fx, fy, scale=0.5):
        mask = np.float32(np.zeros((image_height, image_width, 3)))
        x, y, width, height, rotation = instance["x"], instance["y"], instance["width"]*scale, instance["height"]*scale, instance["rotation"]
        rect = ((x, y), (width, height), rotation)
        cv_box = cv2.boxPoints(rect)
        cv_box = np.int0(cv_box)
        cv2.fillConvexPoly(mask, cv_box, (0,255,0))
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(mask, 100, 1, cv2.THRESH_BINARY)[1]
        mask = mask.astype(bool)
        masked_depth = depth[mask]
        length = np.mean(masked_depth[np.nonzero(masked_depth)])*depth_scale

        return OrientedBoundingBoxDetector.get_ray(image_width, image_height, x, y, fx, fy)*length

    @staticmethod
    def get_point_3d_from_height(instance, camera_height, pick_height,  image_width, image_height, fx, fy):
        x, y = instance["x"], instance["y"]
        plane_C = Plane(point=[0, 0, camera_height-pick_height], normal=[0, 0, -1])
        ray = OrientedBoundingBoxDetector.get_ray(image_width, image_height, x, y, fx, fy)
        line_C = Line([0, 0, 0], ray)
        point_3d_C = plane_C.intersect_line(line_C)
        return np.array(point_3d_C)

    def __call__(self, color):
        predictions = []
        raw_predictions = self.predictor(color)
        raw_bounding_boxes = raw_predictions["instances"].to("cpu").pred_boxes.tensor.numpy()
        for i, raw_bounding_box in enumerate(raw_bounding_boxes):
            instance = {
                "instance_id": i,
                "x": raw_bounding_box[0],
                "y": raw_bounding_box[1],
                "width" : raw_bounding_box[2],
                "height": raw_bounding_box[3],
                "rotation": -raw_bounding_box[4],
            }
            predictions.append(instance)

        return predictions



    




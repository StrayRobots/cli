from detectron2.utils.visualizer import Visualizer
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import os
import cv2
import json

def load_config(flags):
    config = get_cfg()
    if os.path.isfile(os.path.join(flags["model"], "config.yaml")):
        config.merge_from_file(os.path.join(flags["model"], "config.yaml"))
    return config

def evaluate(flags):
    scenes = [scene for scene in flags["dataset"] if os.path.isdir(scene)]
    dataset_metadata_path = os.path.join(flags["model"], "dataset_metadata.json")
    with open(dataset_metadata_path, 'rb') as f:
        dataset_metadata = json.load(f)
    config = load_config(flags)
    
    if flags["weights"] is not None:
        config.MODEL.WEIGHTS = flags["weights"]
    else:
        config.MODEL.WEIGHTS = os.path.join(config.OUTPUT_DIR, "model_final.pth")
    config.MODEL.ROI_HEADS.SCORE_THRESH_TEST = flags["threshold"]
    predictor = DefaultPredictor(config)


    for i, scene_path in enumerate(scenes):
        for image_path in sorted(os.listdir(os.path.join(scene_path, "color"))):
            image = os.path.join(scene_path, "color", image_path)
            im = cv2.imread(image)
            outputs = predictor(im)
            v = Visualizer(im[:, :, ::-1],
                        metadata=dataset_metadata, 
                        scale=1.0
            )
            out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
            image = out.get_image()[:, :, ::-1]
            cv2.imshow("Stray Model Evaluate", image)
            cv2.waitKey(1)



from detectron2.utils.visualizer import Visualizer
from detectron2.engine import DefaultPredictor
from straylib.export import get_detectron2_dataset_function, get_scene_dataset_metadata
from detectron2.config import get_cfg
import os
import cv2
from straymodel.detectron.train import setup_config
import random
import straylib

def evaluate(flags):
    scenes = straylib.utils.get_scene_paths(flags["dataset"])
    dataset_metadata = get_scene_dataset_metadata(scenes)
    dataset_dicts = get_detectron2_dataset_function(scenes, dataset_metadata)()

    config = get_cfg()
    config = setup_config(config, flags, dataset_metadata)

    config.MODEL.WEIGHTS = os.path.join(config.OUTPUT_DIR, "model_final.pth")
    config.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.9
    predictor = DefaultPredictor(config)
    for d in random.sample(dataset_dicts, 100): 
        im = cv2.imread(d["file_name"])
        outputs = predictor(im)
        v = Visualizer(im[:, :, ::-1],
                    metadata=dataset_metadata, 
                    scale=1.5
        )
        out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
        image = out.get_image()[:, :, ::-1]
        cv2.imshow("Stray Model Evaluate", image)
        cv2.waitKey(1)



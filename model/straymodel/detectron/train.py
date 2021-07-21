from detectron2 import model_zoo
from straylib.export import get_detectron2_bbox_dataset_function, get_detectron2_keypoints_dataset_function, get_scene_dataset_metadata
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.engine import default_setup, hooks, launch, DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from .trainer import Trainer
from .utils import logger_setup
import logging
from detectron2.config import get_cfg
import os
import random
import cv2


def train_detectron(flags):
    if os.path.exists(os.path.join(flags["dataset"], 'scene', 'integrated.ply')):
        scenes = [flags["dataset"]]
    else:
        scenes = [os.path.abspath(os.path.join(flags["dataset"], scene)) for scene in os.listdir(flags["dataset"])]
        scenes.sort()
    dataset_metadata = get_scene_dataset_metadata(scenes)
    dataset_name = "stray_dataset"
    config = get_cfg()
    config.OUTPUT_DIR = flags["model_path"]
    config.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_1x.yaml"))
    if flags["primitive"] == "bbox_2d":
        dataset_function = get_detectron2_bbox_dataset_function(scenes)
        MetadataCatalog.get(dataset_name).thing_classes = [f"instance {i}" for i in range(dataset_metadata["num_bbox_categories"] + 1)]
        config.MODEL.ROI_HEADS.NUM_CLASSES = dataset_metadata['num_bbox_categories'] + 1
        config.MODEL.KEYPOINT_ON = False
    elif flags["primitive"] == "keypoints":
        dataset_function = get_detectron2_keypoints_dataset_function(scenes)
        MetadataCatalog.get(dataset_name).keypoint_names = [f"keypoint_{i}" for i in range(dataset_metadata["num_keypoint_categories"])]
        MetadataCatalog.get(dataset_name).keypoint_flip_map = []
        MetadataCatalog.get(dataset_name).keypoint_connection_rules = [(f"keypoint_{i-1}", f"keypoint_{i}", (0, 255, 0))for i in range(1,dataset_metadata["num_keypoint_categories"]+1)]
        MetadataCatalog.get(dataset_name).thing_classes = ["keypoints instance"]
        config['MODEL']['ROI_HEADS']['NUM_CLASSES'] = 1
        config.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = dataset_metadata["num_keypoint_categories"]
    else:
        raise Exception(f"Invalid primitive type (--primitive) provided. Only one of ['keypoints', 'bbox_2d] is currently supported")

    if os.path.isfile(os.path.join(flags["model_path"], "config.yaml")):
        config.merge_from_file(os.path.join(flags["model_path"], "config.yaml"))

    
    DatasetCatalog.register(dataset_name, dataset_function)
    config['DATASETS']['TRAIN'] = (dataset_name,)
    config['DATASETS']['TEST'] = (dataset_name,)

    if flags["num_gpus"] == 0:
        config['MODEL']['DEVICE'] = 'cpu'

    trainer = Trainer(config)
    trainer.resume_or_load(resume=flags["resume"])

    if config.TEST.AUG.ENABLED:
        trainer.register_hooks(
            [hooks.EvalHook(0, lambda: trainer.test_with_TTA(config, trainer.model))]
        )

    trainer.train()


def train(flags):
    launch(
        train_detectron,
        flags["num_gpus"],
        args=(flags,),
    )
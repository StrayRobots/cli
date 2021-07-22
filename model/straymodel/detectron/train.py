from detectron2 import model_zoo
from straylib.export import get_detectron2_dataset_function, get_scene_dataset_metadata
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.engine import hooks, launch
from .trainer import Trainer
from detectron2.config import get_cfg
import os
import straylib

def setup_config(config, flags, metadata):
    config.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_1x.yaml"))
    if os.path.isfile(os.path.join(flags["model_path"], "config.yaml")):
        config.merge_from_file(os.path.join(flags["model_path"], "config.yaml"))
    config.OUTPUT_DIR = os.path.join(flags["model_path"], "output")
    config.MODEL.ROI_HEADS.NUM_CLASSES = len(metadata['instance_category_mapping'])
    if metadata["max_num_keypoints"] == 0:
        config.MODEL.KEYPOINT_ON = False
    else:
        config.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = metadata["max_num_keypoints"]
    if "num_gpus" not in flags.keys() or flags["num_gpus"] == 0:
        config.MODEL.DEVICE = 'cpu'

    return config


def train_detectron(flags):
    scenes = straylib.utils.get_scene_paths(flags["dataset"])
    dataset_metadata = get_scene_dataset_metadata(scenes)
    dataset_function = get_detectron2_dataset_function(scenes, dataset_metadata)

    dataset_name = "stray_dataset"
    MetadataCatalog.get(dataset_name).thing_classes = [name for name in dataset_metadata["instance_category_mapping"].keys()]
    MetadataCatalog.get(dataset_name).keypoint_names = [f"keypoint_{i}" for i in range(dataset_metadata["max_num_keypoints"])]
    MetadataCatalog.get(dataset_name).keypoint_flip_map = []
    MetadataCatalog.get(dataset_name).keypoint_connection_rules = []    
    DatasetCatalog.register(dataset_name, dataset_function)

    config = get_cfg()
    config = setup_config(config, flags, dataset_metadata)
    config.DATASETS.TRAIN = (dataset_name,)
    config.DATASETS.TEST = (dataset_name,)

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
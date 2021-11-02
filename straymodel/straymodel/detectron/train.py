from detectron2 import model_zoo
from straylib.export import get_detectron2_dataset_function, get_scene_dataset_metadata
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.engine import hooks, launch
from straymodel.detectron.trainer import Trainer
from detectron2.config import get_cfg
import os
import json
import yaml

def setup_config(config, flags, metadata):
    if flags["segmentation"]:
        config.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        config.INPUT.MASK_FORMAT = "bitmask"
        config.INPUT.CROP.ENABLED = True
    else:
        config.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_1x.yaml"))
    
    if os.path.isfile(os.path.join(flags["model"], "config.yaml")):
        config.merge_from_file(os.path.join(flags["model"], "config.yaml"))
    config.OUTPUT_DIR = os.path.join(flags["model"], "output")
    config.MODEL.ROI_HEADS.NUM_CLASSES = len(metadata['instance_category_mapping'])
    
    if metadata["max_num_keypoints"] == 0:
        config.MODEL.KEYPOINT_ON = False
    else:
        config.MODEL.ROI_KEYPOINT_HEAD.NUM_KEYPOINTS = metadata["max_num_keypoints"]

    if "num_gpus" not in flags.keys() or flags["num_gpus"] == 0:
        config.MODEL.DEVICE = 'cpu'

    return config

def save_dataset_metadata(flags, metadata):
    with open(os.path.join(flags["model"], "dataset_metadata.json"), 'w') as f:
        json.dump(metadata, f)

def save_config(flags, config):
    with open(os.path.join(flags["model"], 'config.yaml'), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)



def train_detectron(flags):
    scenes = [path for path in flags["dataset"] if os.path.isdir(path)]
    dataset_metadata = get_scene_dataset_metadata(scenes)
    save_dataset_metadata(flags, dataset_metadata)
    dataset_function = get_detectron2_dataset_function(scenes, dataset_metadata, flags["bbox_from_mask"], flags["segmentation"])
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

    save_config(flags, config) 
    
    trainer.train()


def train(flags):
    launch(
        train_detectron,
        flags["num_gpus"],
        args=(flags,),
    )
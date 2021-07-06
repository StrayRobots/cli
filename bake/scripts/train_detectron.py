import argparse
import logging
import os
from collections import OrderedDict
import torch

from detectron2 import model_zoo
from straylib.export import detectron2_dataset_function, scene_dataset_metadata
from detectron2.data import DatasetCatalog
import detectron2.utils.comm as comm
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.engine import DefaultTrainer, default_setup, hooks, launch
from detectron2.evaluation import COCOEvaluator, DatasetEvaluators
from detectron2.modeling import GeneralizedRCNNWithTTA

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('resume', action='store_true')
    parser.add_argument('--num-gpus', type=int, default=1)
    return parser.parse_args()

class Trainer(DefaultTrainer):
    @classmethod
    def build_evaluator(cls, config, dataset_name, output_folder=None):
        if output_folder is None:
            output_folder = os.path.join(config.OUTPUT_DIR, "inference")
        evaluator = COCOEvaluator(dataset_name, output_dir=output_folder)
        return DatasetEvaluators(evaluator)

    @classmethod
    def test_with_TTA(cls, config, model):
        logger = logging.getLogger("detectron2.trainer")
        logger.info("Running inference with test-time augmentation ...")
        model = GeneralizedRCNNWithTTA(config, model)
        evaluators = [
            cls.build_evaluator(
                config, name, output_folder=os.path.join(config.OUTPUT_DIR, "inference_TTA")
            )
            for name in config.DATASETS.TEST
        ]
        res = cls.test(config, model, evaluators)
        res = OrderedDict({k + "_TTA": v for k, v in res.items()})
        return res

def get_config():
    return model_zoo.get_config("COCO-Detection/rpn_R_50_FPN_1x.yaml")

def main(flags):
    flags = read_args()

    dataset_function = detectron2_dataset_function(flags.dataset)
    dataset_metadata = scene_dataset_metadata(flags.dataset)
    DatasetCatalog.register("stray_dataset", dataset_function)

    dataset_name = "stray_dataset"
    data: List[Dict] = DatasetCatalog.get(dataset_name)

    config = get_config()

    config['DATASETS']['TRAIN'] = (dataset_name,)
    config['DATASETS']['TEST'] = (dataset_name,)
    config['MODEL']['ROI_HEADS']['NUM_CLASSES'] = dataset_metadata['num_classes']

    if flags.num_gpus == 0:
        config['MODEL']['DEVICE'] = 'cpu'

    default_setup(config, flags)

    trainer = Trainer(config)
    trainer.resume_or_load(resume=flags.resume)
    if config.TEST.AUG.ENABLED:
        trainer.register_hooks(
            [hooks.EvalHook(0, lambda: trainer.test_with_TTA(config, trainer.model))]
        )
    return trainer.train()

if __name__ == "__main__":
    flags = read_args()
    print("Command line arguments:", flags)
    launch(
        main,
        flags.num_gpus,
        args=(flags,),
    )

import logging
import os
from collections import OrderedDict

from detectron2.engine import DefaultTrainer
from detectron2.evaluation import COCOEvaluator, DatasetEvaluators
from detectron2.modeling import GeneralizedRCNNWithTTA
from detectron2.data import DatasetMapper, build_detection_train_loader
import detectron2.data.transforms as T

def build_augmentations(cfg):
    augs = [
            T.ResizeShortestEdge(
                cfg.INPUT.MIN_SIZE_TRAIN, cfg.INPUT.MAX_SIZE_TRAIN, cfg.INPUT.MIN_SIZE_TRAIN_SAMPLING
            ),
            T.ResizeScale(min_scale=0.1, max_scale=2.0, target_height=cfg.INPUT.MAX_SIZE_TRAIN, target_width=cfg.INPUT.MAX_SIZE_TRAIN),
            T.RandomCrop_CategoryAreaConstraint(
                cfg.INPUT.CROP.TYPE,
                cfg.INPUT.CROP.SIZE,

            ),
            T.RandomFlip()
        ]
    return augs

class Trainer(DefaultTrainer):
    @classmethod
    def build_evaluator(cls, config, dataset_name, output_folder=None):
        if output_folder is None:
            output_folder = os.path.join(config.OUTPUT_DIR, "inference")
        evaluator = COCOEvaluator(dataset_name, output_dir=output_folder)
        return DatasetEvaluators([evaluator])

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

    @classmethod
    def build_train_loader(cls, cfg):
        mapper = DatasetMapper(cfg, is_train=True, augmentations=build_augmentations(cfg))
        return build_detection_train_loader(cfg, mapper=mapper)

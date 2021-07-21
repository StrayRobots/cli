import logging
import os
from collections import OrderedDict

from detectron2.engine import DefaultTrainer
from detectron2.evaluation import COCOEvaluator, DatasetEvaluators
from detectron2.modeling import GeneralizedRCNNWithTTA

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
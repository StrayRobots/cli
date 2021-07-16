from detectron2 import model_zoo
from straylib.export import get_detectron2_dataset_function, scene_dataset_metadata
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.engine import default_setup, hooks, launch, DefaultPredictor
from detectron2.utils.visualizer import Visualizer
from .trainer import Trainer

def get_config():
    return model_zoo.get_config("COCO-Detection/rpn_R_50_FPN_1x.yaml")

def train_detectron(dataset, num_gpus, resume):
    dataset_function = get_detectron2_dataset_function(dataset)
    dataset_metadata = scene_dataset_metadata(dataset)
    dataset_name = "stray_dataset"
    DatasetCatalog.register(dataset_name, dataset_function)
    MetadataCatalog.get(dataset_name).thing_classes = [f"Instance {i}" for i in range(dataset_metadata['num_classes'])]

    dataset_name = "stray_dataset"

    config = get_config()

    config['DATASETS']['TRAIN'] = (dataset_name,)
    config['DATASETS']['TEST'] = (dataset_name,)
    config['MODEL']['ROI_HEADS']['NUM_CLASSES'] = dataset_metadata['num_classes']

    if num_gpus == 0:
        config['MODEL']['DEVICE'] = 'cpu'

    default_setup(config, (dataset, num_gpus, resume))

    trainer = Trainer(config)
    trainer.resume_or_load(resume=resume)
    if config.TEST.AUG.ENABLED:
        trainer.register_hooks(
            [hooks.EvalHook(0, lambda: trainer.test_with_TTA(config, trainer.model))]
        )
    return trainer.train()


def train(dataset, num_gpus, resume):
    launch(
        train_detectron,
        num_gpus,
        args=(dataset, num_gpus, resume),
    )
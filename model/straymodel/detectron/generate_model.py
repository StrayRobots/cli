
import yaml
import os

def generate(model_folder):
    config = dict(
        DATALOADER = dict(
            NUM_WORKERS = 5
        ),
        SOLVER = dict(
            IMS_PER_BATCH = 2,
            BASE_LR = 0.00025,
            MAX_ITER = 10000,
            STEPS = [],
            CHECKPOINT_PERIOD=1000
        ),
        MODEL = dict(
            ROI_HEADS = dict(
                BATCH_SIZE_PER_IMAGE = 128
            )
        ),
        TEST = dict(
            AUG = dict(
                ENABLED = False
            )
        )
    )

    os.makedirs(os.path.join(model_folder,'output'), exist_ok=True)
    with open(os.path.join(model_folder,'config.yaml'), 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

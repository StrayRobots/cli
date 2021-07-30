import click
import os
from straymodel.detectron.train import train as train_detectron

@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--model', required=True, help='Path to the model to use in baking.')
@click.option('--num-gpus', default=0, help='Number of GPUs to use in baking.')
@click.option('--resume', default=False, is_flag=True, help='Resume training.')

def bake(**flags):
    model_name = os.path.basename(os.path.normpath(flags["model"])).split("-")[0]
    if model_name == "detectron2":
        train_detectron(flags)
    else:
        raise Exception(f"Invalid model name prefix for model {flags['model']}. Only detectron2 is currently supported.")

if __name__ == '__main__':
    bake()

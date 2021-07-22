import click
import os
import straymodel

@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--model-path', required=True, help='Path to the model to use in baking.')
@click.option('--num_gpus', default=0, help='Number of GPUs to use in baking.')
@click.option('--resume', default=False, is_flag=True, help='Resume training.')

def bake(**flags):
    model_name = os.path.basename(os.path.normpath(flags["model_path"])).split("-")[0]
    if model_name == "detectron2":
        straymodel.detectron.train.train(flags)
    else:
        raise Exception(f"Invalid model name prefix for model {flags['model_path']}. Only detectron2 is currently supported.")

if __name__ == '__main__':
    bake()

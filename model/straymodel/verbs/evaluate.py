import click
import os
from straymodel.detectron.evaluate import evaluate as evaluate_detectron

@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--model-path', required=True, help='Path to the model to use in baking.')


def evaluate(**flags):
    model_name = os.path.basename(os.path.normpath(flags["model_path"])).split("-")[0]
    if model_name == "detectron2":
        evaluate_detectron(flags)
    else:
        raise Exception(f"Invalid model name prefix for model {flags['model_path']}. Only detectron2 is currently supported.")

if __name__ == '__main__':
    evaluate()
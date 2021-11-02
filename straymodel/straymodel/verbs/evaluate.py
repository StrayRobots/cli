import click
import os
from straymodel.detectron.evaluate import evaluate as evaluate_detectron

@click.command()
@click.argument('dataset', nargs=-1)
@click.option('--model', required=True, help='Path to the model to use in baking.')
@click.option('--weights', help='Override the weights file in model/output. Default is model/output/model_final.pth')
@click.option('--threshold', default=0.7, help='Prediction confidence threshold')


def evaluate(**flags):
    model_name = os.path.basename(os.path.normpath(flags["model"])).split("-")[0]
    if model_name == "detectron2":
        evaluate_detectron(flags)
    else:
        raise Exception(f"Invalid model name prefix for model {flags['model']}. Only detectron2 is currently supported.")

if __name__ == '__main__':
    evaluate()
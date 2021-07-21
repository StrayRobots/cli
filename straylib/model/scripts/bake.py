import click
import os, json
import model

@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--model-path', required=True, help='Path to the model to use in baking.')
@click.option('--primitive', required=True, help='Primitive type to bake into model.')
@click.option('--num_gpus', default=0, help='Number of GPUs to use in baking.')
@click.option('--resume', default=False, is_flag=True, help='Resume training.')

def bake(**flags):
    with open(os.path.join(flags["model_path"], "metadata.json"), 'rt') as f:
        model_metadata = json.load(f)

    if model_metadata['model_type'] == "detectron2":
        model.detectron.train.train(flags)
    else:
        raise Exception(f"Invalid model type (model_type) in metadata.json for model {flags['model_path']}. Only detectron2 is currently supported.")
    
if __name__ == '__main__':
    bake()

import click
import os, json
import straymodel

@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--model-path', required=True, help='Path to the model to use in baking.')
@click.option('--primitive', required=True, help='Primitive type to bake into model.')
@click.option('--num_gpus', default=0, help='Number of GPUs to use in baking.')
@click.option('--resume', default=False, is_flag=True, help='Resume training.')

def bake(dataset, model_path, primitive, num_gpus, resume):
    with open(os.path.join(model_path, "config.json"), 'rt') as f:
        model_config = json.load(f)

    if model_config['model_type'] == "detectron2":
        straymodel.detectron.train.train(dataset, num_gpus, resume)
    else:
        raise Exception(f"Invalid model type (model_type) in config.json for model {model_path}. Only detectron2 is currently supported.")

if __name__ == '__main__':
    bake()

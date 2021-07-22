import click
import os, json
import straymodel
import datetime

@click.command()
@click.option('--model-type',default="detectron2", required=True, help='Type of model to generate.')
@click.option('--path', required=True, help='Path to where the new model is created')


def generate(**flags):
    if flags['model_type'] == "detectron2":
        now = datetime.datetime.now()
        model_suffix = now.strftime("%Y-%m-%d-%H:%M:%S")
        base_folder = os.path.join(flags["path"], f"detectron2-{model_suffix}")
        os.makedirs(base_folder, exist_ok=True)
        straymodel.detectron.generate_model.generate(base_folder)
    else:
        raise Exception(f"Invalid model type (--model-type) provided. Only detectron2 is currently supported.")
    print(f"New model created successfully at {base_folder}")

if __name__ == '__main__':
    generate()
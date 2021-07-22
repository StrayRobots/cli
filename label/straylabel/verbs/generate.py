import argparse
import os
import json
from straylib.export import get_detectron2_dataset_function, get_scene_dataset_metadata
import straylib
import click
import os, json
import straylabel

def write(flags, examples):
    dataset_path = os.path.join(flags["dataset"], 'dataset.json')
    with open(dataset_path, 'wt') as f:
        f.write(json.dumps(examples))

    print(f"Wrote dataset file to {dataset_path}.")


@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--format', default="detectron2", required=True, help='Which dataset format to generate.')
@click.option('--primitive', help='Primitive type labels to create.')
def generate(**flags):
    scenes = straylib.utils.get_scene_paths(flags["dataset"])
    if "primitive" in flags.keys() and flags["primitive"] == "semantic":
        for scene in scenes:
            straylabel.segmentation.segment.segment(scene)
    elif flags["format"] == 'detectron2':
        dataset_metadata = get_scene_dataset_metadata(scenes)
        examples = get_detectron2_dataset_function(scenes, dataset_metadata)()

        write(flags, examples)
    else:
        raise NotImplementedError("Unknown dataset format. The only currently supported format is 'detectron2'.")

if __name__ == "__main__":
    generate()


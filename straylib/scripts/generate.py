import argparse
import os
import json
from straylib.export import detectron2_dataset_function

def read_args():
    parser = argparse.ArgumentParser(description="Convert Stray Scene datasets into other dataset formats.")
    parser.add_argument('scenes_folder', help="The directory where you keep your scenes.")
    parser.add_argument('--format', type=str, default="detectron2", help="Which dataset format to generate.")
    return parser.parse_args()

def write(flags, examples):
    dataset_path = os.path.join(flags.scenes_folder, 'dataset.json')
    with open(dataset_path, 'wt') as f:
        f.write(json.dumps(examples))

    print(f"Wrote dataset file to {dataset_path}.")

def main():
    flags = read_args()
    if flags.format == 'detectron2':
        examples = detectron2_dataset_function(flags.scenes_folder)
        write(flags, examples)
    else:
        raise NotImplementedError("Unknown dataset format. The only currently supported format is 'detectron2'.")

if __name__ == "__main__":
    main()


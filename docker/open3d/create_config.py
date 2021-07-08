import argparse
import json
import os

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('out')
    return parser.parse_args()

def main():
    flags = read_args()

    dataset_path = os.path.abspath(os.path.expanduser(flags.dataset))
    intrinsics_path = os.path.join(dataset_path, 'camera_intrinsics.json')
    config = {
        "name": "Stray Scanner dataset",
        "path_dataset": dataset_path,
        "path_intrinsic": intrinsics_path,
        "depth_scale": 1000.0,
        "max_depth": 10.0,
        "min_depth": 0.05
    }
    with open(os.path.join(flags.out), 'w') as f:
        f.write(json.dumps(config, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()


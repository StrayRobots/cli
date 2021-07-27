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
    # Slac integrate script needs trailing slash.
    if dataset_path[-1] != os.sep:
        dataset_path += os.sep
    intrinsics_path = os.path.join(dataset_path, 'camera_intrinsics.json')
    config = {
        "name": "Stray Scanner dataset",
        "path_dataset": dataset_path,
        "path_intrinsic": intrinsics_path,
        "n_frames_per_fragment": 250,
        "depth_scale": 1000.0,
        "max_depth": 2.0,
        "min_depth": 0.1,
        "max_depth_diff": 0.03,
        "tsdf_cubic_size": 0.75,
        "debug_mode": False,
        "save_output_as": "mesh"
    }
    with open(os.path.join(flags.out), 'w') as f:
        f.write(json.dumps(config, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()


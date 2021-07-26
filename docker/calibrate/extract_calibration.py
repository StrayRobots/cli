import argparse
import yaml
import json

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--calibration', help="The Kalibr camchain calibration file.")
    parser.add_argument('--out', help="Where to place the camera_intrinsics.json output calibration file.")
    return parser.parse_args()

def main():
    flags = read_args()

    with open(flags.calibration, 'rt') as f:
        camchain = yaml.load(f, Loader=yaml.SafeLoader)

    camera = camchain['cam0']
    fx, fy, cx, cy = camera['intrinsics']
    intrinsic_matrix = [fx, 0.0, 0.0, 0.0, fy, 0.0, cx, cy, 1.0]
    distortion_coefficients = camera['distortion_coeffs']

    calibration = {
        'depth_scale': 1000.0,
        'depth_format': 'Z16',
        'width': camera['resolution'][0],
        'height': camera['resolution'][1],
        'intrinsic_matrix': intrinsic_matrix,
        'camera_model': 'pinhole',
        'distortion_model': 'KannalaBrandt',
        'distortion_coefficients': distortion_coefficients
    }

    with open(flags.out, 'wt') as f:
        f.write(json.dumps(calibration, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()


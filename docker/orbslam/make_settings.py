import argparse
import json
import os
import yaml
import numpy as np

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--default-settings', type=str, required=True)
    parser.add_argument('--out', '-o', type=str, default='settings.yaml')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def main():
    flags = read_args()

    with open(flags.default_settings, 'rt') as f:
        f.readline()
        settings = yaml.load(f, Loader=yaml.SafeLoader)

    with open(os.path.join(flags.scene, 'camera_intrinsics.json'), 'rt') as f:
        intrinsics = json.load(f)

    intrinsic_matrix = np.array(intrinsics['intrinsic_matrix']).reshape(3, 3).T
    settings['Camera.fx'] = intrinsic_matrix[0, 0].item()
    settings['Camera.fy'] = intrinsic_matrix[1, 1].item()
    settings['Camera.cx'] = intrinsic_matrix[0, 2].item()
    settings['Camera.cy'] = intrinsic_matrix[1, 2].item()
    settings['Camera.width'] = intrinsics['width']
    settings['Camera.height'] = intrinsics['height']

    settings['DepthMapFactor'] = intrinsics.get('depth_scale', 1000.0)
    settings['Camera.fps'] = intrinsics.get('fps', 30.0)

    if (intrinsics.get('camera_model', 'pinhole').lower() == 'pinhole' and
            intrinsics.get('distortion_model', 'KannalaBrandt').lower() == 'kannalabrandt'):
        distortion_coeffs = intrinsics['distortion_coefficients']
        settings['Camera.type'] = 'KannalaBrandt8'
        settings['Camera.k1'] = distortion_coeffs[0]
        settings['Camera.k2'] = distortion_coeffs[1]
        settings['Camera.k3'] = distortion_coeffs[2]
        settings['Camera.k4'] = distortion_coeffs[3]

    elif (intrinsics.get('camera_model', 'pinhole').lower() == 'pinhole' and
        intrinsics.get('distortion_model', None) == None):
        print("Warning: no distortion coefficients set.")
        settings['Camera.type'] = 'PinHole'
    else:
        raise ValueError("Unknown camera model.")

    with open(flags.out, 'wt') as f:
        # ORBSlam reads the file with opencv which needs this.
        f.write('%YAML:1.0\n\n')

        f.write(yaml.dump(settings))



if __name__ == "__main__":
    main()

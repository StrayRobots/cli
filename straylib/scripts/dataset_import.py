import os
import click
import shutil
import re
import numpy as np
import json
import cv2
from skvideo import io

def _resize_camera_matrix(camera_matrix, scale_x, scale_y):
    if scale_x == 1.0 and scale_y == 1.0:
        return camera_matrix
    fx = camera_matrix[0, 0]
    fy = camera_matrix[1, 1]
    cx = camera_matrix[0, 2]
    cy = camera_matrix[1, 2]
    return np.array([[fx * scale_x, 0.0, cx * scale_x],
        [0., fy * scale_y, cy * scale_y],
        [0., 0., 1.0]])

def write_frames(dataset, every, rgb_out_dir, width, height):
    rgb_video = os.path.join(dataset, 'rgb.mp4')
    video = io.vreader(rgb_video)
    for i, frame in enumerate(video):
        if i % every != 0:
            continue
        print(f"Writing rgb frame {i:06}" + " " * 10, end='\r')
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.resize(frame, (width, height))
        frame_path = os.path.join(rgb_out_dir, f"{i:06}.jpg")
        params = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        cv2.imwrite(frame_path, frame, params)
    return frame.shape[1], frame.shape[0]

def resize_depth(depth, width, height):
    out = cv2.resize(depth, (width, height), interpolation=cv2.INTER_NEAREST_EXACT)
    out[out < 10] = 0
    return out

def write_depth(dataset, every, depth_out_dir, width, height):
    depth_dir_in = os.path.join(dataset, 'depth')
    confidence_dir = os.path.join(dataset, 'confidence')
    files = sorted(os.listdir(depth_dir_in))
    for i, filename in enumerate(files):
        if '.npy' not in filename or i % every != 0:
            continue
        print(f"Writing depth frame {filename}", end='\r')
        number, _ = filename.split('.')
        depth_file = os.path.join(depth_dir_in, filename)
        confidence_file = os.path.join(confidence_dir, number + '.png')
        depth = np.load(depth_file)
        if os.path.exists(confidence_file):
            confidence = cv2.imread(confidence_file)[:, :, 0]
        else:
            confidence = np.ones_like(depth_file, dtype=np.uint8) * 2
        depth[confidence < 2] = 0
        depth = resize_depth(depth, width, height)
        cv2.imwrite(os.path.join(depth_out_dir, number + '.png'), depth)

def write_intrinsics(dataset, out, width, height, full_width, full_height):
    intrinsics = np.loadtxt(os.path.join(dataset, 'camera_matrix.csv'), delimiter=',')
    data = {}
    intrinsics_scaled = _resize_camera_matrix(intrinsics, width / full_width, height / full_height)
    data['intrinsic_matrix'] = [intrinsics_scaled[0, 0], 0.0, 0.0,
            0.0, intrinsics_scaled[1, 1], 0.0,
            intrinsics_scaled[0, 2], intrinsics_scaled[1, 2], 1.0]
    data['width'] = width
    data['height'] = height
    data['depth_scale'] = 1000.0
    data['fps'] = 60.0
    data['depth_format'] = 'Z16'
    with open(os.path.join(out, 'camera_intrinsics.json'), 'wt') as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))

@click.command()
@click.argument('scenes', nargs=-1)
@click.option('--out', '-o', required=True, help="Dataset directory where to place the imported files.", type=str)
@click.option('--every', type=int, default=1, help="Keep only every n-th frame. 1 keeps every frame, 2 keeps every other and so forth.")
@click.option('--width', '-w', type=int, default=640)
@click.option('--height', '-h', type=int, default=480)
@click.option('--intrinsics', type=str, help="Path to the intrinsic parameters to use (for example calibrated parameters from stray calibration run). Defaults to factory parameters.")
def main(scenes, out, every, width, height, intrinsics):
    """
    Command for importing scenes from the Stray Scanner format to the Stray Dataset format.

    Usage: import <scanner-scenes> --out <output-dataset-folder>

    Each scene will be imported and converted into the dataset folder.
    """
    os.makedirs(out, exist_ok=True)
    existing_scenes = os.listdir(out)
    for scene_path in scenes:
        scene_base_name = os.path.basename(scene_path)
        if scene_base_name[0] == ".":
            continue
        if scene_base_name in existing_scenes:
            print(f"Scene {scene_base_name} exists already, skipping.")
            continue
        target_path = os.path.join(out, scene_base_name)
        print(f"Importing scene {scene_path} into {target_path}")

        rgb_out = os.path.join(target_path, 'color/')
        depth_out = os.path.join(target_path, 'depth/')
        os.makedirs(rgb_out)
        os.makedirs(depth_out)

        write_depth(scene_path, every, depth_out, width, height)
        full_width, full_height = write_frames(
            scene_path, every, rgb_out, width, height)
        write_intrinsics(scene_path, target_path, width,
                         height, full_width, full_height)
        shutil.copy(os.path.join(scene_path, 'rgb.mp4'), os.path.join(target_path, 'rgb.mp4'))

        if intrinsics is None:
            if os.path.exists(os.path.join(scene_path, 'camera_matrix.csv')):
                print("Writing factory intrinsics.", end='\n')
                write_intrinsic_params(scene_path, target_path, width, height, full_width, full_height)
            else:
                print("Warning: no camera matrix found, skipping.")
         else:
            print("Writing intrinsics.", end='\n')
            shutil.copy(intrinsics, os.path.join(target_path, 'camera_intrinsics.json'))

    print("Done.")

if __name__ == "__main__":
    main()



import argparse
import os
import math
import json
import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation
from stray.camera import scale_intrinsics
from stray.scene import Scene

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--voxel-size', type=float, default=0.005)
    return parser.parse_args()

def read_image(color_file, depth_file):
    color = o3d.io.read_image(color_file)
    depth = o3d.io.read_image(depth_file)
    depth_width, _ = depth.get_max_bound()
    width, _ = color.get_max_bound()
    scale = depth_width / width
    color = o3d.t.geometry.Image.from_legacy(color)
    color = color.resize(scale, o3d.t.geometry.InterpType.Linear)

    return o3d.geometry.RGBDImage.create_from_color_and_depth(
        color.to_legacy(),
        depth,
        depth_scale=1000,
        depth_trunc=2.5,
        convert_rgb_to_intensity=False)

def show_frames(poses):
    frames = [o3d.geometry.TriangleMesh.create_coordinate_frame().scale(0.25, np.zeros(3))]
    for pose_id, T_WC in poses:
        if pose_id % 60 != 0:
            continue
        print(f"Frame {pose_id}", end="\r")
        mesh = o3d.geometry.TriangleMesh.create_coordinate_frame().scale(0.1, np.zeros(3))
        frames.append(mesh.transform(T_WC))
    return frames

def filename(path):
    return os.path.splitext(os.path.basename(path))[0]

def create_fragment(trajectory, color_images, depth_images, intrinsics, voxel_size):
    fragment = o3d.geometry.PointCloud()
    depth_image = o3d.io.read_image(depth_images[0])
    intrinsics_scaled = scale_intrinsics(intrinsics, *depth_image.get_max_bound())
    rgbd = read_image(color_images[0], depth_images[0])
    for i, (T_WC, color, depth) in enumerate(zip(trajectory, color_images, depth_images)):
        if not os.path.exists(color) or not os.path.exists(depth):
            continue
        print(f"reading frame {i}", end='\r')
        assert filename(color) == filename(depth)
        rgbd = read_image(color, depth)
        fragment += o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsics_scaled, extrinsic=np.linalg.inv(T_WC))

    return fragment.voxel_down_sample(voxel_size)

def select_views(scene, fps):
    count = len(scene)
    if count < 200:
        return np.arange(count)
    else:
        return np.arange(0, count, max(int(fps / 4.0), 1))

def main():
    flags = read_args()

    scene = Scene(flags.scene)
    camera_matrix = scene.camera_matrix
    intrinsics = o3d.camera.PinholeCameraIntrinsic(scene.frame_width, scene.frame_height, camera_matrix[0, 0],
            camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2])
    trajectory = np.stack(scene.poses)
    color_images = scene.get_image_filepaths()
    depth_images = scene.get_depth_filepaths()

    scene_cloud = o3d.geometry.PointCloud()

    with open(os.path.join(scene.scene_path, 'camera_intrinsics.json'), 'rt') as f:
        data = json.load(f)
        fps = data.get('fps', 30)

    view_indices = select_views(scene, fps)

    scene_cloud += create_fragment(trajectory[view_indices],
            [color_images[i] for i in view_indices],
            [depth_images[i] for i in view_indices],
            intrinsics,
            voxel_size=flags.voxel_size)

    o3d.io.write_point_cloud(os.path.join(flags.scene, 'scene', 'cloud.ply'), scene_cloud)

if __name__ == "__main__":
    main()

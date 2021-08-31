import argparse
import os
import math
import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation
from straylib.scene import Scene

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--frames-per-fragment', '-f', type=int, default=50)
    parser.add_argument('--voxel-size', type=float, default=0.025)
    return parser.parse_args()

def read_image(color_file, depth_file):
    color = o3d.io.read_image(color_file)
    depth = o3d.io.read_image(depth_file)
    return o3d.geometry.RGBDImage.create_from_color_and_depth(
        color,
        depth,
        depth_scale=1000,
        depth_trunc=3.0,
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
    for i, (pose, color, depth) in enumerate(zip(trajectory, color_images, depth_images)):
        print(f"reading frame {i}", end='\r')
        assert filename(color) == filename(depth)
        rgbd = read_image(color, depth)
        pointcloud = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, intrinsics, extrinsic=np.linalg.inv(pose))
        fragment += pointcloud

    return fragment.voxel_down_sample(voxel_size)

def main():
    flags = read_args()

    scene = Scene(flags.scene)
    camera_matrix = scene.camera_matrix
    intrinsics = o3d.camera.PinholeCameraIntrinsic(scene.frame_width, scene.frame_height, camera_matrix[0, 0],
            camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2])
    trajectory = scene.poses
    color_images = scene.image_filepaths()
    depth_images = scene.depth_filepaths()

    scene_cloud = o3d.geometry.PointCloud()
    n_frames = min(len(color_images), len(depth_images))
    n_fragments = math.ceil(n_frames / flags.frames_per_fragment)
    for fragment_index in range(n_fragments):
        start = fragment_index * flags.frames_per_fragment
        end = (fragment_index+1) * flags.frames_per_fragment
        print(f"Integrating fragment {fragment_index+1:03} / {n_fragments:03}")
        fragment = create_fragment(trajectory[start:end], color_images[start:end], depth_images[start:end],
                intrinsics,
                voxel_size=flags.voxel_size)
        scene_cloud += fragment

    scene_cloud = scene_cloud.voxel_down_sample(flags.voxel_size)
    o3d.io.write_point_cloud(os.path.join(flags.scene, 'scene', 'cloud.ply'), scene_cloud)

if __name__ == "__main__":
    main()

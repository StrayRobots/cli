import argparse
import os
import numpy as np
import json
from scipy.spatial.transform import Rotation
import copy
from straylib.scene import Scene
import utils

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--colmap-dir', required=True)
    return parser.parse_args()

def write_trajectory(poses, flags):
    with open(os.path.join(flags.scene, 'scene', 'trajectory.log'), 'wt') as f:
        for i, (pose_id, pose) in enumerate(poses):
            if i+1 < len(poses):
                next_id = poses[i+1][0]
            else:
                next_id = "{:06}".format(len(poses))
            f.write(f"{pose_id} {pose_id} {next_id}\n")
            for row_index in range(4):
                row = pose[row_index]
                f.write(f"{row[0]} {row[1]} {row[2]} {row[3]}\n")


def read_colmap_trajectory(path):
    images = utils.read_images_bin(os.path.join(path, 'images.bin'))
    images.sort(key=lambda x: x['image_filename'])
    return [(i['image_filename'].split('.')[0], i['T_WC']) for i in images]

def compute_relative_transormation(T_1W, T_2W):
    T_21 = T_2W @ np.linalg.inv(T_1W)
    return T_21

def find_cameras_sfm(cache):
    sfm_dir = os.path.join(cache, 'StructureFromMotion')
    cache_ids = os.listdir(sfm_dir)
    for cache_id in cache_ids:
        cameras_path = os.path.join(sfm_dir, cache_id, 'cameras.sfm')
        if not os.path.exists(cameras_path):
            continue
        return cameras_path

def compute_average_scale_diff(slam_trajectory, colmap_trajectory):
    N = len(slam_trajectory)
    assert N == len(colmap_trajectory)
    translations_slam = np.stack([T[:3, 3] for _, T in slam_trajectory])
    translations_sfm = np.stack([T[:3, 3] for _, T in colmap_trajectory])

    # Calculate difference between subsequent keyframes in slam vs. sfm. Figure
    # out what the scale difference is from these.
    distances_slam = np.zeros(N-1)
    distances_colmap = np.zeros(N-1)
    for i in range(N-1):
        distances_slam[i] = np.linalg.norm(translations_slam[i+1] - translations_slam[i])
        distances_colmap[i] = np.linalg.norm(translations_sfm[i+1] - translations_sfm[i])
    return np.abs(distances_slam / distances_colmap).mean()

def scale_trajectory(trajectory, scale):
    out = []
    for k, T in trajectory:
        T_scaled = T.copy()
        T_scaled[:3, 3] = scale * T[:3, 3]
        out.append((k, T_scaled))
    return out

def align_slam_trajectory(slam_poses, colmap_trajectory):
    """
    Fix the slam trajectory such that each segment between keyframes
    starts exactly at the previous keyframe and tracks from there.
    Could do something fancier where we morph the tracked trajectory such that it
    both starts and ends at the keyframe poses.
    """
    aligned_poses = slam_poses.copy()
    for i, (pose_id, T_WP) in enumerate(colmap_trajectory):
        if i+1 >= len(colmap_trajectory):
            segment_slice = slice(int(pose_id), len(aligned_poses))
        else:
            next_pose_id = colmap_trajectory[i+1][0]
            segment_slice = slice(int(pose_id), int(next_pose_id))
        segment = slam_poses[segment_slice]

        # Make segment relative to first pose in the segment.
        T_IW = np.linalg.inv(segment[0])
        segment = [T_IW @ T for T in segment]

        # Transfer segment to track starting from the last keyframe.
        segment = [T_WP @ T for T in segment]
        aligned_poses[segment_slice] = segment

    return aligned_poses




def main():
    flags = read_args()

    scene = Scene(flags.scene)
    color_images = scene.get_image_filepaths()
    pose_ids = [os.path.basename(i).split('.')[0] for i in color_images]

    colmap_trajectory = read_colmap_trajectory(flags.colmap_dir)

    trajectory_dict = dict([(i, p) for i, p in enumerate(scene.poses)])
    slam_trajectory = [(k, trajectory_dict[int(k)]) for k, v in colmap_trajectory]

    average_scale_difference = compute_average_scale_diff(slam_trajectory, colmap_trajectory)
    colmap_trajectory = scale_trajectory(colmap_trajectory, average_scale_difference)

    # Fix the poses such that the first pose is the origin in both cases.
    T_IW = np.linalg.inv(scene.poses[0])
    slam_trajectory = [T_IW @ T for T in scene.poses]

    T_IW = np.linalg.inv(colmap_trajectory[0][1])
    colmap_trajectory = [(k, T_IW @ T) for k, T in colmap_trajectory]

    poses_aligned = align_slam_trajectory(slam_trajectory, colmap_trajectory)

    write_trajectory(list(enumerate(poses_aligned)), flags)

    # from straylib.debugger import VisualDebugger
    # debugger = VisualDebugger()

    # for _, T in colmap_trajectory:
    #     debugger.add_frame(T)
    # # for T in slam_trajectory[::15]:
    # #     debugger.add_frame(T, color=np.array([0.0, 1.0, 0.0]))

    # for T in poses_aligned:
    #     debugger.add_frame(T, color=np.array([0.0,0.0, 1.0]))
    # debugger.show()

if __name__ == "__main__":
    main()


import argparse
import os
import numpy as np
import json
from scipy.spatial.transform import Rotation
import copy
from straylib.scene import Scene

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
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


def read_meshroom_trajectory(path):
    poses = []
    with open(path) as f:
        data = json.load(f)

    for pose in data["poses"]:
        pose_id = pose["poseId"]
        for view in data["views"]:
            if view["poseId"] == pose_id:
                filename = os.path.basename(view["path"])
                image_idx = filename.split('.')[0]
                transformation = pose["pose"]["transform"]
                rotation_flat = np.array(transformation["rotation"])
                rotation = rotation_flat.reshape(3,3)
                translation = np.array(transformation["center"])
                T = np.eye(4)
                T[:3, :3] = rotation
                T[:3, 3] = translation
                poses.append((image_idx, T))
    return sorted(poses)

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

def compute_average_scale_diff(slam_trajectory, meshroom_trajectory):
    N = len(slam_trajectory)
    assert N == len(meshroom_trajectory)
    translations_slam = np.stack([T[:3, 3] for _, T in slam_trajectory])
    translations_meshroom = np.stack([T[:3, 3] for _, T in meshroom_trajectory])

    # Calculate difference between subsequent keyframes in slam vs. meshroom. Figure
    # out what the scale difference is from these.
    distances_slam = np.zeros(N-1)
    distances_meshroom = np.zeros(N-1)
    for i in range(N-1):
        distances_slam[i] = np.linalg.norm(translations_slam[i+1] - translations_slam[i])
        distances_meshroom[i] = np.linalg.norm(translations_meshroom[i+1] - translations_meshroom[i])
    return np.abs(distances_slam / distances_meshroom).mean()

def scale_trajectory(trajectory, scale):
    out = []
    for k, T in trajectory:
        T_scaled = T.copy()
        T_scaled[:3, 3] = scale * T[:3, 3]
        out.append((k, T_scaled))
    return out

def align_slam_trajectory(slam_poses, meshroom_trajectory):
    """
    Fix the slam trajectory such that each segment between keyframes
    starts exactly at the previous keyframe and tracks from there.
    Could do something fancier where we morph the tracked trajectory such that it
    both starts and ends at the keyframe poses.
    """
    aligned_poses = slam_poses.copy()
    for i, (pose_id, T_WP) in enumerate(meshroom_trajectory):
        if i+1 >= len(meshroom_trajectory):
            segment_slice = slice(int(pose_id), len(aligned_poses))
        else:
            next_pose_id = meshroom_trajectory[i+1][0]
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

    meshroom_trajectory_path = find_cameras_sfm(os.path.join(flags.scene, 'MeshroomCache'))
    meshroom_trajectory = read_meshroom_trajectory(meshroom_trajectory_path)

    trajectory_dict = dict([(i, p) for i, p in enumerate(scene.poses)])
    slam_trajectory = [(k, trajectory_dict[int(k)]) for k, v in meshroom_trajectory]

    average_scale_difference = compute_average_scale_diff(slam_trajectory, meshroom_trajectory)
    meshroom_trajectory = scale_trajectory(meshroom_trajectory, average_scale_difference)

    # Fix the poses such that the first pose is the origin in both cases.
    T_IW = np.linalg.inv(scene.poses[0])
    slam_trajectory = [T_IW @ T for T in scene.poses]

    T_IW = np.linalg.inv(meshroom_trajectory[0][1])
    meshroom_trajectory = [(k, T_IW @ T) for k, T in meshroom_trajectory]

    poses_aligned = align_slam_trajectory(slam_trajectory, meshroom_trajectory)

    write_trajectory(list(enumerate(poses_aligned)), flags)


if __name__ == "__main__":
    main()

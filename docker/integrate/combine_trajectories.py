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


def main():
    flags = read_args()

    scene = Scene(flags.scene)
    color_images = scene.get_image_filepaths()
    pose_ids = [os.path.basename(i).split('.')[0] for i in color_images]

    meshroom_trajectory_path = find_cameras_sfm(os.path.join(flags.scene, 'MeshroomCache'))
    meshroom_trajectory = read_meshroom_trajectory(meshroom_trajectory_path)

    trajectory_dict = dict([(i, p) for i, p in enumerate(scene.poses)])

    T = meshroom_trajectory[0][1] #Transform slam frames to start from first meshroom frame

    origin_translation = T[:3, 3]
    scales = []

    #Calculate average scale of matched frames between slam / meshroom
    for i in range(0, len(meshroom_trajectory)):
        mr_T_0X = meshroom_trajectory[i][1]
        pose_id = int(meshroom_trajectory[i][0])
        if pose_id in trajectory_dict:
            slam_T_0X = copy.deepcopy(trajectory_dict[pose_id])
            slam_T_0X_prescale = T @ slam_T_0X
            mr_translation = mr_T_0X[:3, 3]
            slam_translation = slam_T_0X_prescale[:3, 3]
            diff_slam_origin = np.linalg.norm(slam_translation-origin_translation)
            if np.linalg.norm(diff_slam_origin) < 1e-6:
                calculated_scale = 1.0
            else:
                calculated_scale = (np.linalg.norm(mr_translation-origin_translation) / diff_slam_origin)
            scales.append(calculated_scale)


    scale = np.mean(scales)
    fixed_poses = []
    slam_T_0X = T
    lost_count = 0

    #Transform slam frames to meshroom coordinates and scale
    for pose_id in pose_ids:
        if int(pose_id) in trajectory_dict:
            slam_T_0X = trajectory_dict[int(pose_id)]
            slam_T_0X[:3, 3] *= scale
            slam_T_0X = T @ slam_T_0X
        else:
            print("Lost pose", lost_count, pose_id)
            lost_count += 1
        fixed_poses.append((pose_id, slam_T_0X))

    write_trajectory(fixed_poses, flags)





if __name__ == "__main__":
    main()

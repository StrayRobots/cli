import argparse
import os
import numpy as np
import json
from scipy.spatial.transform import Rotation
import copy

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    return parser.parse_args()

def read_trajectory(path):
    poses = []
    trajectory = np.loadtxt(path, delimiter=' ')
    for line in trajectory:
        ts, tx, ty, tz, qx, qy, qz, qw = line
        pose_id = int(ts)
        rotation = Rotation.from_quat([qx, qy, qz, qw])
        T = np.eye(4)
        T[:3, :3] = rotation.as_matrix()
        T[:3, 3] = [tx, ty, tz]
        poses.append((pose_id, T))
    return poses

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

def main():
    flags = read_args()

    color_images = os.listdir(os.path.join(flags.scene, 'color'))
    pose_ids = [i.split('.')[0] for i in color_images]
    pose_ids.sort()

    trajectory_path = os.path.join(flags.scene, "CameraTrajectory.txt")
    meshroom_trajectory_path = os.path.join(flags.scene, "cameras.sfm")


    meshroom_trajectory = read_meshroom_trajectory(meshroom_trajectory_path)

    if not os.path.exists(trajectory_path):
        write_trajectory(meshroom_trajectory, flags)
        return

    trajectory = read_trajectory(trajectory_path)
    trajectory_dict = dict(trajectory)

    T = meshroom_trajectory[0][1] #Transform slam frames to start from first meshroom frame

    origin_translation = T[:3, 3]
    scales = []

    #Calculate average scale of matched frames between slam / meshroom
    for i in range(0, len(meshroom_trajectory)):
        mr_T_0X = meshroom_trajectory[i][1]
        pose_id = int(meshroom_trajectory[i][0])
        if pose_id in trajectory_dict.keys():
            slam_T_0X = copy.deepcopy(trajectory_dict[pose_id])
            slam_T_0X_prescale = T @ slam_T_0X
            mr_translation = mr_T_0X[:3, 3]
            slam_translation = slam_T_0X_prescale[:3, 3]
            calculated_scale = np.linalg.norm(mr_translation-origin_translation)/np.linalg.norm(slam_translation-origin_translation)
            scales.append(calculated_scale)


    scale = np.mean(scales)
    fixed_poses = []
    slam_T_0X = T
    lost_count = 0

    #Transform slam frames to meshroom coordinates and scale
    for pose_id in pose_ids:
        if int(pose_id) in trajectory_dict.keys():
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

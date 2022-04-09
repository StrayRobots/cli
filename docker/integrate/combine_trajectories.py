import argparse
import os
import numpy as np
import json
import pycolmap
import cv2
from stray import linalg
from scipy.spatial.transform import Rotation
import open3d as o3d
import copy
from stray.scene import Scene
import csv
import utils

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--colmap-dir', required=True)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def write_trajectory(poses, flags):
    scene_dir = os.path.join(flags.scene, 'scene')
    os.makedirs(scene_dir, exist_ok=True)
    with open(os.path.join(scene_dir, 'trajectory.log'), 'wt') as f:
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

def scale_trajectory(trajectory, scale):
    out = []
    for k, T in trajectory:
        T_scaled = T.copy()
        T_scaled[:3, 3] = scale * T[:3, 3]
        out.append((k, T_scaled))
    return out

def align_trajectories(slam_poses, colmap_trajectory):
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

class ScaleEstimator:
    min_depth = 1e-2
    def __init__(self, scene, colmap_dir, vio_trajectory, colmap_trajectory):
        self.scene = scene
        self.colmap_dir = colmap_dir
        self.vio_trajectory = vio_trajectory
        self.frames = [i[0] for i in colmap_trajectory]
        self.colmap_frames = [i[1] for i in colmap_trajectory]
        self.colmap_trajectory = dict(colmap_trajectory)
        self.reconstruction = pycolmap.Reconstruction(colmap_dir)
        self._read_depth_maps()

    def _read_depth_maps(self):
        self.depth_maps = {}
        frame_numbers = set(self.frames)
        for path in self.scene.get_depth_filepaths():
            frame_number = os.path.basename(path).split('.')[0]
            if frame_number in frame_numbers:
                self.depth_maps[frame_number] = cv2.imread(path, -1) / 1000.0
        depth_shape = next(iter(self.depth_maps.values())).shape
        depth_size = np.array([depth_shape[1], depth_shape[0]], dtype=np.float64)
        self.depth_to_color_ratio = depth_size / np.array(self.scene.camera().size, dtype=np.float64)

    def _lookup_depth(self, frame, xy):
        xy_depth = np.floor(self.depth_to_color_ratio * xy).astype(int)
        return self.depth_maps[frame][xy_depth[1], xy_depth[0]]

    def estimate(self):
        images = self.reconstruction.images
        point_depths = []
        measured_depths = []
        for image_id, image in images.items():
            frame_number = image.name.split('.')[0]
            points = image.get_valid_points2D()
            points3D = self.reconstruction.points3D
            for point in points:
                depth_map_value = self._lookup_depth(frame_number, point.xy)

                if depth_map_value < self.min_depth:
                    continue

                T_WC = self.colmap_trajectory[frame_number]
                point3D = points3D[point.point3D_id]

                T_CW = np.linalg.inv(T_WC)
                p_C = linalg.transform_points(T_CW, point3D.xyz)
                measured_depths.append(depth_map_value)
                point_depths.append(p_C[2])

        point_depths = np.stack(point_depths)
        measured_depths = np.stack(measured_depths)
        scales = measured_depths / point_depths
        return self._ransac(scales)

    def _ransac(self, scales):
        best_set = None
        best_inlier_count = 0
        indices = np.arange(0, scales.shape[0])
        inlier_threshold = np.median(scales) * 1e-2
        for i in range(10000):
            selected = np.random.choice(indices)
            estimate = scales[selected]
            inliers = np.abs(scales - estimate) < inlier_threshold
            inlier_count = inliers.sum()
            if inlier_count > best_inlier_count:
                best_set = scales[inliers]
                best_inlier_count = inlier_count
        print(f"Scale estimation inlier count: {best_inlier_count} / {scales.size}")
        lower_percentile = np.percentile(scales, 10)
        upper_percentile = np.percentile(scales, 90)
        scales = scales[np.bitwise_and(scales > lower_percentile, scales < upper_percentile)]
        return np.mean(scales)

def read_pointcloud(depth_image, intrinsic, T_WC):
    depth = o3d.geometry.Image(cv2.imread(depth_image, -1))
    return o3d.geometry.PointCloud.create_from_depth_image(depth, intrinsic, extrinsic=np.linalg.inv(T_WC),
            depth_scale=1000.0)

def main():
    flags = read_args()

    scene = Scene(flags.scene)
    color_images = scene.get_image_filepaths()
    pose_ids = [os.path.basename(i).split('.')[0] for i in color_images]
    vio_poses = utils.read_vio_trajectory(flags.scene)

    colmap_trajectory = read_colmap_trajectory(flags.colmap_dir)

    trajectory_dict = dict([(i, p) for i, p in enumerate(vio_poses)])
    vio_trajectory = [(k, trajectory_dict[int(k)]) for k, v in colmap_trajectory]

    scale_estimator = ScaleEstimator(scene, flags.colmap_dir, vio_trajectory, colmap_trajectory)
    scale_diff = scale_estimator.estimate()
    colmap_trajectory = scale_trajectory(colmap_trajectory, scale_diff)

    # Fix the poses such that the first pose is the origin in both cases.
    T_IW = np.linalg.inv(vio_poses[0])
    vio_trajectory = [T_IW @ T for T in vio_poses]

    T_IW = np.linalg.inv(colmap_trajectory[0][1])
    colmap_trajectory = [(k, T_IW @ T) for k, T in colmap_trajectory]

    poses_aligned = align_trajectories(vio_trajectory, colmap_trajectory)

    if flags.debug:
        from stray.debugger import VisualDebugger
        visualizer = VisualDebugger()
        camera = scene.camera()
        depth_images = scene.get_depth_filepaths()
        depth = cv2.imread(depth_images[0], -1)
        camera = camera.scale((depth.shape[1], depth.shape[0]))
        intrinsics = o3d.camera.PinholeCameraIntrinsic(camera.size[0], camera.size[1], camera.camera_matrix[0, 0], camera.camera_matrix[1, 1],
                camera.camera_matrix[0, 2], camera.camera_matrix[1, 2])
        for T_WC in vio_trajectory:
            visualizer.add_frame(T_WC, color=(1.0, 0.0, 0.0))
        for _, T_WC in colmap_trajectory:
            visualizer.add_frame(T_WC, color=(0.0, 1.0, 0.0))
        visualizer.show()

    write_trajectory(list(enumerate(poses_aligned)), flags)

if __name__ == "__main__":
    main()


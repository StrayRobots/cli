import argparse
import os
import numpy as np
import open3d as o3d
import csv
import warnings
from stray.scene import Scene
from scipy.spatial.transform import Rotation

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--voxel-size', default=0.005, type=float)
    parser.add_argument('--trajectory', '-t')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def read_frames_csv(scene_path, pose_ids):
    path = os.path.join(scene_path, 'frames.csv')
    poses = {}
    with open(path, 'rt') as f:
        reader = csv.reader(f)
        header = next(reader)
        for line in reader:
            x, y, z, qx, qy, qz, qw = [float(f) for f in line[2:9]]
            pose = np.eye(4)
            pose[:3, 3] = [x, y, z]
            pose[:3, :3] = Rotation.from_quat([qx, qy, qz, qw]).as_matrix()
            pose_id = line[1]
            poses[int(pose_id)] = pose
    return [(pose_id, poses[int(pose_id)]) for pose_id in pose_ids]

def read_trajectory_log(scene_path):
    scene = Scene(scene_path)
    return [(f"{i:06}", T) for i, T in enumerate(scene.poses)]

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

def read_image(color_file, depth_file):
    color = o3d.io.read_image(color_file)
    depth = o3d.io.read_image(depth_file)
    depth_width, _ = depth.get_max_bound()
    width, _ = color.get_max_bound()
    depth = o3d.t.geometry.Image.from_legacy(depth)
    scale = width / depth_width
    depth = depth.resize(scale, o3d.t.geometry.InterpType.Nearest)

    return o3d.geometry.RGBDImage.create_from_color_and_depth(
        color,
        depth.to_legacy(),
        depth_scale=1000,
        depth_trunc=5,
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

def main():
    flags = read_args()
    scene_path = flags.scene

    intrinsic = o3d.io.read_pinhole_camera_intrinsic(os.path.join(scene_path, 'camera_intrinsics.json'))

    color_images = os.listdir(os.path.join(flags.scene, 'color'))
    pose_ids = [i.split('.')[0] for i in color_images if '.jpg' in i]
    pose_ids.sort()

    trajectory_path = os.path.join(flags.scene, 'scene', 'trajectory.log')
    if os.path.exists(trajectory_path):
        poses = read_trajectory_log(flags.scene)
    else:
        poses = read_frames_csv(flags.scene, pose_ids)
        os.makedirs(os.path.join(flags.scene, 'scene'), exist_ok=True)
        write_trajectory(poses, flags)


    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=flags.voxel_size, # In meters.
        sdf_trunc=0.04,
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)

    for pose_id, T in poses:
        print(f"Integrating {pose_id}", end='\r')
        color_image = os.path.join(scene_path, 'color', f'{pose_id}.jpg')
        depth_image = os.path.join(scene_path, 'depth', f'{pose_id}.png')
        if not os.path.exists(color_image):
            warnings.warn(f"Color image {pose_id}.jpg not found. Skipping frame.")
            continue
        if not os.path.exists(depth_image):
            warnings.warn(f"Depth image {pose_id}.png not found. Skipping frame.")
            continue
        rgbd_frame = read_image(color_image, depth_image)
        volume.integrate(rgbd_frame, intrinsic, np.linalg.inv(T))

    mesh = volume.extract_triangle_mesh()
    mesh.compute_vertex_normals()
    if flags.debug:
        frames = show_frames(poses)
        o3d.visualization.draw_geometries([mesh] + frames)

    o3d.io.write_triangle_mesh(os.path.join(flags.scene, 'scene', 'integrated.ply'), mesh, False, True)


if __name__ == "__main__":
    main()

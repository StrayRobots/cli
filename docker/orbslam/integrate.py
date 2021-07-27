import argparse
import os
import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--trajectory', '-t')
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def read_trajectory(pose_ids, path):
    poses = []
    trajectory = np.loadtxt(path, delimiter=' ')
    for pose_id, line in zip(pose_ids, trajectory):
        ts, tx, ty, tz, qx, qy, qz, qw = line
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

def main():
    flags = read_args()
    scene_path = flags.scene

    intrinsic = o3d.io.read_pinhole_camera_intrinsic(os.path.join(scene_path, 'camera_intrinsics.json'))

    color_images = os.listdir(os.path.join(flags.scene, 'color'))
    pose_ids = [i.split('.')[0] for i in color_images]
    pose_ids.sort()

    poses = read_trajectory(pose_ids, flags.trajectory)
    os.makedirs(os.path.join(flags.scene, 'scene'), exist_ok=True)
    write_trajectory(poses, flags)
    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=0.01, # In meters.
        sdf_trunc=0.04,
        color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8)

    for pose_id, T in poses:
        print(f"Integrating {pose_id}", end='\r')
        color_image = os.path.join(scene_path, 'color', f'{pose_id}.jpg')
        depth_image = os.path.join(scene_path, 'depth', f'{pose_id}.png')
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

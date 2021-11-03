import argparse
import os
import numpy as np
import json
import trimesh
import shutil



def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    return parser.parse_args()

def read_meshroom_intrinsics(path):
    with open(path) as f:
        data = json.load(f)

    meshroom_intrinsics = data["intrinsics"][0]

    intrisics = {}
    intrisics["fps"] = 60.0
    intrisics["height"] = float(meshroom_intrinsics["height"])
    intrisics["width"] = float(meshroom_intrinsics["width"])
    intrisics["intrinsic_matrix"] = [float(meshroom_intrinsics["pxFocalLength"]), 0.0, 0.0, 0.0, float(meshroom_intrinsics["pxFocalLength"]), 0.0, float(meshroom_intrinsics["principalPoint"][0]), float(meshroom_intrinsics["principalPoint"][1]), 1.0]
    intrisics["distortion_coefficients"] = [float(i) for i in meshroom_intrinsics["distortionParams"]]
    
    return intrisics

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



def main():
    flags = read_args()

    sfm_path = os.path.join(flags.scene, "MeshroomCache", "StructureFromMotion")
    sfm_dir = os.listdir(sfm_path)[0]
    meshroom_trajectory_path =  os.path.join(sfm_path, sfm_dir, "cameras.sfm")

    mesh_dir_path = os.path.join(flags.scene, "MeshroomCache", "Texturing")
    mesh_dir = os.listdir(mesh_dir_path)[0]
    mesh_path =  os.path.join(mesh_dir_path, mesh_dir, "texturedMesh.obj")

    intrinsics = read_meshroom_intrinsics(meshroom_trajectory_path)

    with open(os.path.join(flags.scene, 'camera_intrinsics.json'), 'wt') as f:
        f.write(json.dumps(intrinsics, indent=4, sort_keys=True))

    os.makedirs(os.path.join(flags.scene, "scene"), exist_ok=True)

    mesh = trimesh.load(mesh_path)
    mesh.visual = mesh.visual.to_color()
    trimesh.exchange.export.export_mesh(mesh, os.path.join(flags.scene, "scene", "integrated.ply"), file_type="ply", resolver=None)
    shutil.copy(meshroom_trajectory_path, os.path.join(flags.scene, "cameras.sfm"))



if __name__ == "__main__":
    main()
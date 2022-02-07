import argparse
import os
import json
import shutil
import numpy as np
import subprocess
import sqlite3
from straylib.scene import Scene
from scipy.spatial.transform import Rotation

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene', help="Stray Scene to use.")
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()

def read_json(path):
    with open(path, 'rt') as f:
        return json.load(f)

def array_to_blob(array):
    return array.tobytes()

class Runner:
    def __init__(self):
        self.flags = read_args()
        self.scene = Scene(self.flags.scene)
        self._read_scene_metadata()
        self.intrinsics_id = 1
        os.makedirs('/tmp/sfm', exist_ok=True)
        self.tmp_dir = '/tmp/sfm'
        self.sparse_dir = '/tmp/sfm/sparse'
        self.database_path = '/tmp/sfm/database.db'
        self.out_path = '/tmp/sfm/sfm'
        self.image_list_path = os.path.join(self.sparse_dir, 'image_list.txt')

    def _read_scene_metadata(self):
        camera_intrinsics = read_json(os.path.join(self.flags.scene, 'camera_intrinsics.json'))
        self.fps = camera_intrinsics.get('fps', 30.0)

    def _select_viewpoints(self):
        total_count = len(self.scene)
        if total_count < 50:
            self.selected_views = np.arange(len(self.scene))
        else:
            self.selected_views = np.arange(0, len(self.scene), int(self.fps / 4.0))

    def _create_database(self):
        subprocess.run(['colmap', 'database_creator', '--database_path', self.database_path])

    def _create_cameras_txt(self):
        camera = self.scene.camera()
        K = camera.camera_matrix
        width = camera.size[0]
        height = camera.size[1]
        with open(os.path.join(self.sparse_dir, 'cameras.txt'), 'wt') as f:
            fx = K[0, 0]
            fy = K[1, 1]
            cx = K[0, 2]
            cy = K[1, 2]
            D = camera.distortion
            f.write(f"{self.intrinsics_id} OPENCV {width} {height} {fx} {fy} {cx} {cy} {D[0]} {D[1]} {D[2]} {D[3]}\n")

    def _create_images_txt(self):
        c = sqlite3.connect(self.database_path)
        color_images = self.scene.get_image_filepaths()
        with open(os.path.join(self.sparse_dir, 'images.txt'), 'wt') as images_txt:
            poses = self.scene.poses
            for index, image_index in enumerate(self.selected_views.tolist()):
                image = color_images[image_index]
                T_WC = poses[image_index]
                R_WC = Rotation.from_matrix(T_WC[:3, :3])
                q = R_WC.as_quat()
                xyz = T_WC[:3, 3]
                name = os.path.basename(image)
                images_txt.write(f"{index} {q[3]} {q[0]} {q[1]} {q[2]} {xyz[0]} {xyz[1]} {xyz[2]} {self.intrinsics_id} {name}\n\n")

                c.execute("INSERT INTO images VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (index, name, self.intrinsics_id, q[3], q[0], q[1], q[2], xyz[0], xyz[1], xyz[2]))
        c.commit()
        with open(self.image_list_path, 'wt') as image_list:
            for i in self.selected_views.tolist():
                image = os.path.basename(color_images[i])
                image_list.write(f"{image}\n")

    def _add_camera_to_database(self):
        c = sqlite3.connect(self.database_path)
        OPENCV_MODEL_ID = 4
        camera = self.scene.camera()
        width = camera.size[0]
        height = camera.size[1]
        K = camera.camera_matrix
        fx = K[0, 0]
        fy = K[1, 1]
        cx = K[0, 2]
        cy = K[1, 2]
        D = camera.distortion
        params = np.array([fx, fy, cx, cy, D[0], D[1], D[2], D[3]])
        blob = array_to_blob(params)
        c.execute("INSERT INTO cameras VALUES (?, ?, ?, ?, ?, ?)",
                (self.intrinsics_id, OPENCV_MODEL_ID, width, height, blob, False))
        c.commit()

    def _copy_images(self):
        color_images = self.scene.get_image_filepaths()
        os.makedirs(self.color_path, exist_ok=True)
        for i in self.selected_views.tolist():
            image = color_images[i]

            basename = os.path.basename(image)
            out_path = os.path.join(self.tmp_dir, 'color', basename)
            shutil.copy(image, out_path)

    def _create_points3d(self):
        with open(os.path.join(self.sparse_dir, 'points3D.txt'), 'wt') as f:
            f.write("")

    def _run_sfm(self):
        color_path = os.path.join(self.scene.scene_path, 'color')
        extractor = subprocess.run(['colmap', 'feature_extractor', '--database_path', self.database_path,
            '--SiftExtraction.use_gpu=false',
            '--image_path', color_path,
            '--image_list', self.image_list_path])
        if extractor.returncode != 0:
            print("Feature extraction failed.")
            exit(1)
        if len(self.selected_views) < 200:
            matcher = 'exhaustive_matcher'
        else:
            matcher = 'sequential_matcher'
        match_result = subprocess.run(['colmap', matcher, '--database_path', self.database_path,
            '--SiftMatching.use_gpu=false'])
        if match_result.returncode != 0:
            print("Image matching failed.")
            exit(1)

        mapping_result = subprocess.run(['colmap', 'mapper', '--database_path', self.database_path,
            '--image_path', color_path,
            '--output_path', self.out_path])
        if mapping_result.returncode != 0:
            print("Mapping failed.")
            exit(1)

    def _move_sfm_dir(self):
        shutil.move('/tmp/sfm/', os.path.join(self.flags.scene, 'sfm'))

    def run(self):
        shutil.rmtree(self.tmp_dir)
        os.makedirs(self.sparse_dir)
        os.makedirs(self.out_path)
        self._select_viewpoints()
        self._create_database()
        self._create_cameras_txt()
        self._add_camera_to_database()
        self._create_images_txt()
        self._create_points3d()
        self._run_sfm()
        if self.flags.debug:
            self._move_sfm_dir()


if __name__ == "__main__":
    Runner().run()

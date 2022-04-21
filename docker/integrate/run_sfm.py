import argparse
import os
import json
import shutil
import numpy as np
import subprocess
import sqlite3
import utils
import pycolmap
from pathlib import Path
from stray.scene import Scene
from scipy.spatial.transform import Rotation
from hloc import extract_features, match_features, reconstruction, visualization, pairs_from_exhaustive, pairs_from_retrieval
from hloc.utils import viz_3d


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene', help="Stray Scene to use.")
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--vis', action='store_true')
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
        self.exhaustive = True

        self.tmp_dir = Path('/tmp/sfm/')
        self.tmp_dir.mkdir(exist_ok=True)
        self.sfm_pairs = self.tmp_dir / 'sfm-pairs.txt'
        self.loc_pairs = self.tmp_dir / 'sfm-pairs-loc.txt'
        self.features = self.tmp_dir / 'features.h5'
        self.matches = self.tmp_dir / 'matches.h5'
        self.feature_conf = extract_features.confs['superpoint_aachen']
        self.retrieval_conf = extract_features.confs['netvlad']
        self.matcher_conf = match_features.confs['superglue']

    def _read_scene_metadata(self):
        camera_intrinsics = read_json(os.path.join(self.flags.scene, 'camera_intrinsics.json'))
        self.fps = camera_intrinsics.get('fps', 30.0)

    def _select_viewpoints(self):
        total_count = len(self.scene)
        if total_count < 300:
            self.selected_views = np.arange(len(self.scene))
        else:
            self.selected_views = np.arange(0, len(self.scene), max(int(self.fps / 4.0), 1))
        if self.selected_views.size > 200:
            self.exhaustive = False

    def _run_sfm(self):
        images = Path(self.scene.scene_path) / 'color'
        image_list = []
        image_paths = self.scene.get_image_filepaths()
        image_list_path = []
        for index in self.selected_views:
            image_list.append(image_paths[index])
            image_list_path.append(str(Path(image_paths[index]).relative_to(images)))
        if self.exhaustive:
            extract_features.main(self.feature_conf, images, feature_path=self.features, image_list=image_list_path)
            pairs_from_exhaustive.main(self.sfm_pairs, image_list=image_list_path)
            match_features.main(self.matcher_conf, self.sfm_pairs, features=self.features, matches=self.matches)
            model = reconstruction.main(self.tmp_dir, images, self.sfm_pairs, self.features, self.matches, image_list=image_list_path,
                    camera_mode=pycolmap.CameraMode.SINGLE)
        else:
            retrieval_path = extract_features.main(self.retrieval_conf, images, self.tmp_dir, image_list=image_list_path)
            pairs_from_retrieval.main(retrieval_path, self.sfm_pairs, num_matched=10)
            feature_path = extract_features.main(self.feature_conf, images, self.tmp_dir, image_list=image_list_path)
            match_path = match_features.main(self.matcher_conf, self.sfm_pairs, self.feature_conf['output'], self.tmp_dir, matches=self.matches)
            model = reconstruction.main(self.tmp_dir, images, self.sfm_pairs, feature_path, match_path, image_list=image_list_path,
                    camera_mode=pycolmap.CameraMode.SINGLE)

        if self.flags.vis:
            fig = viz_3d.init_figure()
            viz_3d.plot_reconstruction(fig, model, color='rgba(255,0,0,0.5)', name="mapping")
            fig.show()


    def run(self):
        shutil.rmtree(str(self.tmp_dir))
        self._select_viewpoints()
        self._run_sfm()
        if self.flags.debug:
            shutil.move("/tmp/sfm/", "/home/user/data/sfm/")


if __name__ == "__main__":
    Runner().run()

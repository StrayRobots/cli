import argparse
import json
import numpy as np
from stray.scene import Scene

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene', help="Stray Scene to use.")
    parser.add_argument('--out', required=True, help="Where to write cameraInit.sfm file.")
    return parser.parse_args()

def read_json(path):
    with open(path, 'rt') as f:
        return json.load(f)

class Runner:
    def __init__(self):
        self.flags = read_args()
        self.scene = Scene(self.flags.scene)
        self.camera_init = { "version": [1, 0, 0] }
        self.intrinsics_id = 1

    def _set_intrinsics(self):
        camera = self.scene.camera()
        camera_matrix = camera.camera_matrix
        pinhole = False
        if (camera.distortion < 1e16).all():
            pinhole = True
        entry = {
            "intrinsicId": self.intrinsics_id,
            "pxInitialFocalLength": (camera_matrix[0, 0] + camera_matrix[1, 1]) / 2.0,
            "pxFocalLength": (camera_matrix[0, 0] + camera_matrix[1, 1]) / 2.0,
            "width": camera.size[0],
            "height": camera.size[1],
            "type": "pinhole",
            "principalPoint": [str(camera_matrix[0, 2]), str(camera_matrix[1, 2])],
            "distortionParams": [],
            "initializationMode": "calibrated",
            "locked": False
        }
        if pinhole:
            entry['type'] = 'pinhole'
        else:
            raise NotImplementedError("Camera model not implemented yet.")
        self.camera_init['intrinsics'] = [entry]

    def _select_viewpoints(self):
        total_count = len(self.scene)
        if total_count < 50:
            self.selected_views = np.arange(len(self.scene))
        else:
            self.selected_views = np.arange(0, len(self.scene), 30)

    def _set_viewpoints(self):
        entries = []
        color_images = self.scene.get_image_filepaths()
        for i in self.selected_views.tolist():
            image = color_images[i]
            entries.append({
                "poseId": i,
                "viewId": i,
                "intrinsicId": self.intrinsics_id,
                "path": image,
                "metadata": {}
            })
        self.camera_init['views'] = entries

    def _save_file(self):
        with open(self.flags.out, 'wt') as f:
            json.dump(self.camera_init, f, indent=2)

    def run(self):
        self._select_viewpoints()
        self._set_intrinsics()
        self._set_viewpoints()
        self._save_file()


if __name__ == "__main__":
    Runner().run()

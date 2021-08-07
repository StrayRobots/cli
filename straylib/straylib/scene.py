import os
import json
import numpy as np
import trimesh
from PIL import Image
from scipy.spatial.transform import Rotation
from straylib import camera

class BoundingBox:
    def __init__(self, data):
        self.position = np.array(data['position'])
        self.dimensions = np.array(data['dimensions'])
        q = data['orientation']
        self.orientation = Rotation.from_quat([q['x'], q['y'], q['z'], q['w']])
        self.instance_id = data.get('instance_id', 0)

    def cut(self, mesh):
        """
        Cuts the background out of the mesh, removing anything outside the bounding box.
        mesh: trimesh mesh
        returns: trimesh mesh for object
        """
        object_mesh = mesh
        axes = np.eye(3)
        for direction in [-1.0, 1.0]:
            for i, axis in enumerate(axes):
                normal = direction * self.orientation.apply(axis * 0.5)
                origin = self.position + normal * self.dimensions[i]
                object_mesh = trimesh.intersections.slice_mesh_plane(object_mesh, -normal, origin)
        return object_mesh

    def background(self, mesh):
        """
        Cuts the object out of the mesh, removing everything inside the bounding box.
        mesh: trimesh mesh
        returns: trimesh mesh for background
        """
        axes = np.eye(3)
        background = trimesh.Trimesh()
        for direction in [-1.0, 1.0]:
            for i, axis in enumerate(axes):
                normal = direction * self.orientation.apply(axis * 0.5)
                origin = self.position + normal * self.dimensions[i]
                outside = trimesh.intersections.slice_mesh_plane(mesh, normal, origin)
                background = trimesh.util.concatenate(background, outside)
        return background


class Keypoint:
    def __init__(self, data):
        self.instance_id = data.get('instance_id', 0)
        self.position = data['position']

class Scene:
    def __init__(self, path):
        self.scene_path = path
        mesh_file = os.path.join(path, 'scene', 'integrated.ply')
        self.mesh = trimesh.load(mesh_file)
        self._read_annotations()
        self._bounding_boxes = None
        self._keypoints = None
        self._poses = None
        self._metadata = None
        self._read_intrinsics()

    def _read_annotations(self):
        annotation_file = os.path.join(self.scene_path, 'annotations.json')
        if not os.path.exists(annotation_file):
            self.annotations = {}
        with open(annotation_file, 'rt') as f:
            self.annotations = json.load(f)

    def _read_trajectory(self):
        self._poses = []
        with open(os.path.join(self.scene_path, 'scene', 'trajectory.log'), 'rt') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 5):
                rows = [np.fromstring(l, count=4, sep=' ') for l in lines[i+1:i+5]]
                self._poses.append(np.stack(rows))

    def _read_intrinsics(self):
        with open(os.path.join(self.scene_path, 'camera_intrinsics.json')) as f:
            camera_data = json.load(f)
        self.camera_matrix = np.array(camera_data['intrinsic_matrix']).reshape(3, 3).T
        self.frame_width = camera_data['width']
        self.frame_height = camera_data['height']

    def _process_annotations(self):
        self._bounding_boxes = []
        for bbox in self.annotations.get('bounding_boxes', []):
            self._bounding_boxes.append(BoundingBox(bbox))
        self._keypoints = []
        for keypoint in self.annotations.get('keypoints', []):
            self._keypoints.append(Keypoint(keypoint))

    def __len__(self):
        return len(self.poses)

    def camera(self):
        return camera.Camera(self.camera_matrix, np.zeros(4))

    @property
    def poses(self):
        if self._poses is None:
            self._read_trajectory()
        return self._poses

    @property
    def bounding_boxes(self):
        if self._bounding_boxes is None:
            self._process_annotations()
        return self._bounding_boxes

    @property
    def keypoints(self):
        if self._keypoints is None:
            self._process_annotations()
        return self._keypoints

    @property
    def bbox_categories(self):
        categories = []
        for b in self.bounding_boxes:
            if not b.instance_id in categories:
                categories.append(b.instance_id)
        return categories

    @property
    def keypoint_categories(self):
        categories = []
        for k in self.keypoints:
            if not k.instance_id in categories:
                categories.append(k.instance_id)
        return categories

    @property
    def metadata(self):
        metadata_path = os.path.join(self.scene_path, "metadata.json")
        if os.path.exists(metadata_path) and self._metadata is None:
            with open(metadata_path, 'rt') as f:
                self._metadata = json.load(f)
        return self._metadata

    def image_filepaths(self):
        paths = os.listdir(os.path.join(self.scene_path, 'color'))
        paths = [path for path in paths if path.lower().split(".")[-1] in ['png', 'jpg', 'jpeg']]
        paths.sort()
        return list(map(lambda p: os.path.join(self.scene_path, 'color', p), paths))

    def image_size(self):
        images = self.image_filepaths()
        return Image.open(images[0]).size

    def objects(self):
        """
        Returns a trimesh for each bounding box in the scene.
        returns: list[trimesh.Mesh]
        """
        objects = []
        for bbox in self.bounding_boxes:
            object_mesh = bbox.cut(self.mesh)
            objects.append(object_mesh)
        return objects

    def background(self):
        background = self.mesh
        for bbox in self.bounding_boxes:
            background = bbox.background(self.mesh)
        return background


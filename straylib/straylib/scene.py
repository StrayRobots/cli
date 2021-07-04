import os
import json
import numpy as np
import trimesh
import pyrender
from matplotlib import cm
from scipy.spatial.transform import Rotation

R_ogl_cv = np.array([[1.0, 0.0, 0.0],
    [0.0, -1.0, 0.0],
    [0.0, 0.0, -1.0]])
T_ogl_cv = np.eye(4)
T_ogl_cv[:3, :3] = R_ogl_cv

segmentation_colors = cm.tab10(np.linspace(0, 1, 10))[:, :3]

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
        self._read_annotations(path)
        self._read_trajectory()
        self._read_intrinsics()
        self._process_annotations()

    def _read_annotations(self, path):
        annotation_file = os.path.join(path, 'annotations.json')
        if not os.path.exists(annotation_file):
            self.annotations = {}
        with open(annotation_file, 'rt') as f:
            self.annotations = json.load(f)

    def _read_trajectory(self):
        self.poses = []
        with open(os.path.join(self.scene_path, 'scene', 'trajectory.log'), 'rt') as f:
            lines = f.readlines()
            for i in range(0, len(lines), 5):
                rows = [np.fromstring(l, count=4, sep=' ') for l in lines[i+1:i+5]]
                self.poses.append(np.stack(rows))

    def _read_intrinsics(self):
        with open(os.path.join(self.scene_path, 'camera_intrinsics.json')) as f:
            camera_data = json.load(f)
        self.camera_matrix = np.array(camera_data['intrinsic_matrix']).reshape(3, 3).T
        self.frame_width = camera_data['width']
        self.frame_height = camera_data['height']

    def _process_annotations(self):
        self.bounding_boxes = []
        for bbox in self.annotations.get('bounding_boxes', []):
            self.bounding_boxes.append(BoundingBox(bbox))
        self.keypoints = []
        for keypoint in self.annotations.get('keypoints', []):
            self.keypoints.append(Keypoint(keypoint))

    def __len__(self):
        return len(self.poses)

    def objects(self):
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

class Renderer:
    def __init__(self, scene):
        self.scene = scene
        self.renderer = pyrender.OffscreenRenderer(viewport_width=self.scene.frame_width,
                    viewport_height=self.scene.frame_height, point_size=1.0)
        self.camera = pyrender.IntrinsicsCamera(scene.camera_matrix[0, 0], scene.camera_matrix[1, 1],
                scene.camera_matrix[0, 2], scene.camera_matrix[1, 2])
        self._build_pyrender_scene()

    def _build_pyrender_scene(self):
        self.render_scene = pyrender.Scene(ambient_light=[0.02, 0.02, 0.02], bg_color=[1.0, 1.0, 1.0])
        light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=2.0)
        self.camera_node = pyrender.Node(camera=self.camera, matrix=T_ogl_cv)
        self.render_scene.add(light)
        self.render_scene.add_node(self.camera_node)
        self.bg_node = pyrender.Node(pyrender.Mesh.from_trimesh(self.scene.background()))
        self.render_scene.add_node(self.bg_node)
        self.object_nodes = []
        for obj in self.scene.objects():
            node = pyrender.Node(mesh=pyrender.Mesh.from_trimesh(obj))
            self.render_scene.add_node(node)
            self.object_nodes.append(node)

    def update_camera_position(self, new_position):
        self.render_scene.remove_node(self.camera_node)
        self.camera_node = pyrender.Node(camera=self.camera, matrix=new_position)
        self.render_scene.add_node(self.camera_node)

    def render_depth(self, frame_index):
        camera_pose = self.scene.poses[frame_index]
        self.update_camera_position(T_ogl_cv @ camera_pose)
        return self.renderer.render(self.render_scene, flags=pyrender.RenderFlags.DEPTH_ONLY)

    def render_segmentation(self, frame_index, colors=False):
        """
        Renders the semantic segmentation map for camera pose at index frame.
        If colors is set to true, will return a HxWx3 colored image instead of a HxW pixel to instance id matrix.
        """
        camera_pose = self.scene.poses[frame_index]
        self.update_camera_position(camera_pose @ T_ogl_cv)
        segmentation = {
            self.bg_node: (0.0, 0.0, 0.0),
        }
        for bbox, node in zip(self.scene.bounding_boxes, self.object_nodes):
            c = segmentation_colors[bbox.instance_id]
            segmentation[node] = (c[0], c[1], c[2])
        seg, _ = self.renderer.render(self.render_scene, seg_node_map=segmentation, flags=pyrender.RenderFlags.SEG)
        seg = seg[:, :, 2]
        if not colors:
            return seg
        else:
            out = np.zeros((seg.shape[0], seg.shape[1], 3))
            out[seg == 0, :] = np.array([0, 0, 0])
            for bbox in self.scene.bounding_boxes:
                out[seg == (1 + bbox.instance_id), :] = segmentation_colors[bbox.instance_id]

            return (out * 255.0).round().astype(np.uint8)


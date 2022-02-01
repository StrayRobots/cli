import os
from straylib.scene import Scene
import shutil
import argparse
import yaml
import numpy as np
from straylib.export import bbox_2d_from_bbox_3d, bbox_2d_from_mesh

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', help='Dataset to use for training')
    parser.add_argument('--validation', '--val', help="Dataset to use for validation.")
    parser.add_argument('--out', help="Where to save the exported dataset.")
    parser.add_argument('--use-corners', action='store_true',
            help="Create 2D bounding boxes from the 3D bounding corners instead of the scene mesh.")
    return parser.parse_args()

def _get_labels(scene, image, image_index, use_corners=False, objects=None):
    camera = scene.camera()
    T_WC = scene.poses[image_index]
    bboxes = []
    for i, bounding_box in enumerate(scene.bounding_boxes):
        if use_corners:
            bbox = bbox_2d_from_bbox_3d(camera, T_WC, bounding_box)
        else:
            object_mesh = objects[i]
            bbox = bbox_2d_from_mesh(camera, T_WC, object_mesh)
        bboxes.append((bounding_box, bbox))
    return bboxes

def _write_label(scene, instance_id, bbox2d, label_file):
    bbox2d = np.array(bbox2d)
    camera = scene.camera()
    size = np.array(camera.size, dtype=np.float64)
    upper_left = bbox2d[:2]
    lower_right = bbox2d[2:]
    center = (upper_left + lower_right) / 2.0
    width = lower_right[0] - upper_left[0]
    height = lower_right[1] - upper_left[1]
    center_relative = center / size
    width_relative = width / size[0]
    height_relative = height / size[1]
    label_file.write(f"{instance_id} {center_relative[0]} {center_relative[1]} {width_relative} {height_relative}\n")

class DatasetExporter:
    """
    Exports dataset in yolo format.
    """
    def __init__(self, flags):
        self.flags = flags
        self.train_dir = os.path.join(flags.out, 'train')
        self.val_dir = os.path.join(flags.out, 'val')
        self._gather_scenes()

    def _gather_scenes(self):
        train_dataset = self.flags.train
        train_scenes = [os.path.join(train_dataset, d) for d in os.listdir(train_dataset)]
        self.train_scenes = [p for p in train_scenes if os.path.isdir(p)]
        val_dataset = self.flags.validation
        val_scenes = [os.path.join(val_dataset, d) for d in os.listdir(val_dataset)]
        self.val_scenes = [p for p in val_scenes if os.path.isdir(p)]

    def _gather_metadata(self):
        class_ids = set()
        for scene_dir in self.train_scenes:
            scene = Scene(scene_dir)
            for box in scene.bounding_boxes:
                class_ids.add(box.instance_id)
        classes = [c for c in class_ids]
        class_names = [f"Class {i}" for i in range(max(classes) + 1)]
        return {
            'classes': classes,
            'class_names': class_names # TODO: get from dataset metadata if present.
        }

    def _process_scenes(self, input_scenes, out_image_dir):
        i = 0
        for scene_dir in input_scenes:
            scene = Scene(scene_dir)
            images = scene.get_image_filepaths()
            objects = None
            if not self.flags.use_corners:
                objects = []
                for bounding_box in scene.bounding_boxes:
                    objects.append(bounding_box.cut(scene.mesh))

            for image_index, image in enumerate(images):
                ext = image.split('.')[-1]
                filename = f"{i:08}"
                out_image_path = os.path.join(out_image_dir, f"{filename}.{ext}")
                print(f"Exporting image {out_image_path}", end='\r')
                shutil.copy(image, out_image_path)
                labels = _get_labels(scene, image, image_index, use_corners=self.flags.use_corners,
                        objects=objects)
                label_file = os.path.join(out_image_dir, f"{filename}.txt")
                with open(label_file, 'wt') as f:
                    for bbox3d, bbox2d in labels:
                        _write_label(scene, bbox3d.instance_id, bbox2d, f)
                i += 1
        print("")


    def run(self):
        os.makedirs(self.train_dir, exist_ok=True)
        os.makedirs(self.val_dir, exist_ok=True)

        self._process_scenes(self.train_scenes, self.train_dir)
        self._process_scenes(self.val_scenes, self.val_dir)
        metadata = self._gather_metadata()
        num_classes = max(metadata['classes']) + 1
        out = {}
        out['train'] = os.path.join(self.train_dir)
        out['val'] = os.path.join(self.val_dir)
        out['nc'] = num_classes
        out['names'] = metadata['class_names']

        with open(os.path.join(self.flags.out, 'dataset.yaml'), 'wt') as f:
            f.write(yaml.dump(out))


def main():
    return DatasetExporter(read_args()).run()

if __name__ == "__main__":
    main()









import os
import cv2
import numpy as np
from straylib.export import bbox_2d_from_bbox_3d, bbox_2d_from_mesh
from straylib.scene import Scene
import click


@click.command()
@click.argument('dataset', nargs=-1)
@click.option('--primitive', default="bbox_2d", help='Primitive type labels to show/create.')
@click.option('--bbox-from-mesh', default=False, is_flag=True, help='Use the mesh to determine the bounding box')
@click.option('--save', default=False, is_flag=True, help='Save labeled examples to <scene>/<primitive>.')
@click.option('--rate', '-r', default=30.0, help="Frames per second to show frames.")
def show(**flags):
    if flags["primitive"] != 'bbox_2d':
        raise NotImplementedError(f"Unknown label type {flags['primitive']}.")

    title = "Stray Label Show"
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(title, cv2.WND_PROP_TOPMOST, 1)

    print("Playing through images.", end="\r")
    paused = False

    wait_time = int(1000.0 / flags["rate"])
    for scene_path in flags["dataset"]:
        if not os.path.isdir(scene_path):
            continue
        if flags["save"]:
            labeled_save_path = os.path.join(scene_path, flags["primitive"])
            os.makedirs(labeled_save_path, exist_ok=True)
        scene = Scene(scene_path)
        camera = scene.camera()
        bboxes = scene.bounding_boxes
        objects = scene.objects()
        for image_path, T_WC in zip(scene.get_image_filepaths(), scene.poses):
            filename = os.path.basename(image_path)
            print(f"Image {filename}" + " " * 10, end='\r')
            image = cv2.imread(image_path)

            for obj, bbox in zip(objects, bboxes):
                if flags["box_from_mesh"]:
                    bbox_flat = bbox_2d_from_mesh(camera, T_WC, obj)
                else:
                    bbox_flat = bbox_2d_from_bbox_3d(camera, T_WC, bbox)
                bbox_np = np.array(bbox_flat).round().astype(np.int).reshape(2, 2)
                upper_left = bbox_np[0]
                lower_right = bbox_np[1]
                cv2.rectangle(image, tuple(upper_left - 3), tuple(lower_right + 3), (130, 130, 235), 2)

            if flags["save"]:
                cv2.imwrite(os.path.join(labeled_save_path, os.path.basename(image_path.rstrip("/"))), image)

            cv2.imshow(title, image)
            key = cv2.waitKey(wait_time)
            if key == ord('q'):
                break
            elif key == ord(' '):
                paused = not paused

            while paused:
                key = cv2.waitKey(wait_time)
                if key == ord(' '):
                    paused = not paused
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show()


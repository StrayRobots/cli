import os
import cv2
import numpy as np
from straylib.export import get_detectron2_dataset_function, get_scene_dataset_metadata
import click
from straylib.utils import get_scene_paths

@click.command()
@click.option('--dataset', required=True, help='Path to the dataset to bake.')
@click.option('--primitive', default="bbox_2d", help='Primitive type labels to create.')
@click.option('--rate', '-r', default=30.0, help="Frames per second to show frames.")

def show(**flags):
    scenes = get_scene_paths(flags["dataset"])
    dataset_metadata = get_scene_dataset_metadata(scenes)
    examples = get_detectron2_dataset_function(scenes, dataset_metadata)()

    if flags["primitive"] != 'bbox_2d':
        raise NotImplementedError(f"Unknown label type {flags['primitive']}.")

    title = "Stray Label Show"
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(title, cv2.WND_PROP_TOPMOST, 1)

    print("Playing through images.", end="\r")
    paused = False

    wait_time = int(1000.0 / flags["rate"])
    for example in examples:
        key = cv2.waitKey(wait_time)
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused

        while paused:
            key = cv2.waitKey(wait_time)
            if key == ord(' '):
                paused = not paused

        filename = os.path.basename(example["file_name"])
        print(f"Image {filename}" + " " * 10, end='\r')
        image = cv2.imread(example["file_name"])
        for annotation in example["annotations"]:
            bbox = np.array(annotation["bbox"]).round().astype(np.int).reshape(2, 2)
            upper_left = bbox[0]
            lower_right = bbox[1]
            cv2.rectangle(image, tuple(upper_left - 3), tuple(lower_right + 3), (130, 130, 235), 3)
        cv2.imshow(title, image)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    show()


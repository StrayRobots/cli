import argparse
import os
import json
import cv2
import numpy as np
import time
from straylib.export import get_detectron2_dataset_function

def read_args():
    parser = argparse.ArgumentParser(description="A small program to preview 2d bounding box labels.")
    parser.add_argument('dataset_folder', help="The directory where you keep your scenes or a path to a single scene.")
    parser.add_argument('--label', type=str, default="bbox_2d", help="The type of label to visualize.")
    parser.add_argument('--rate', '-r', default=30.0, type=float, help="Frames per second to show frames.")
    return parser.parse_args()

def main():
    flags = read_args()
    examples = get_detectron2_dataset_function(flags.dataset_folder)()

    if flags.label != 'bbox_2d':
        raise NotImplementedError(f"Unknown label type {flags.label}.")

    title = "Bounding Boxes"
    cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(title, cv2.WND_PROP_TOPMOST, 1)

    print("Playing through images.", end="\r")
    paused = False

    wait_time = int(1000.0 / flags.rate)
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
            bbox = np.array(annotation["bbox"]).round().astype(np.int)
            upper_left = bbox[0]
            lower_right = bbox[1]
            cv2.rectangle(image, tuple(upper_left - 3), tuple(lower_right + 3), (130, 130, 235), 3)
        cv2.imshow(title, image)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


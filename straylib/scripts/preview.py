import argparse
import os
import json
import cv2
import numpy as np
import time
from straylib.export import detectron2_dataset_function

def read_args():
    parser = argparse.ArgumentParser(description="Convert Stray Scene datasets into a detectron2 dataset")
    parser.add_argument('scenes_folder', help="The directory where you keep your scenes.")
    parser.add_argument('--label', type=str, default="bbox_2d", help="The type of label to visualize.")
    parser.add_argument('--rate', '-r', type=float, help="Frames per second to show frames.")
    return parser.parse_args()

def main():
    flags = read_args()
    examples = detectron2_dataset_function(flags.scenes_folder)

    if flags.label != 'bbox_2d':
        raise NotImplementedError(f"Unknown label type {flags.label}.")

    title = "Bounding Boxes"
    window = cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    cv2.setWindowProperty(title, cv2.WND_PROP_TOPMOST, 1)
    print("Playing through images.", end="\r")
    for example in examples:
        filename = os.path.basename(example["file_name"])
        print(f"Image {filename}" + " " * 10, end='\r')
        image = cv2.imread(example["file_name"])
        for annotation in example["annotations"]:
            bbox = np.array(annotation["bbox"]).round().astype(np.int)
            upper_left = bbox[0]
            lower_right = bbox[1]
            cv2.rectangle(image, tuple(upper_left - 3), tuple(lower_right + 3), (130, 130, 235), 3)
        cv2.imshow(title, image)
        key = cv2.waitKey(int(1000.0 / flags.rate))
        if key == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


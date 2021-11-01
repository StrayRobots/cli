from __future__ import print_function
import os
import argparse
import sys
import rosbag
import rospy
import cv2
import numpy as np
import json
import csv
from tf import transformations
from geometry_msgs.msg import TransformStamped
from cv_bridge import CvBridge
from tf2_msgs.msg import TFMessage

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--base-frame', default='base_frame')
    parser.add_argument('--hand-frame', default='hand_frame')
    return parser.parse_args()

def read_frame_metadata(flags):
    out = {}
    frames_csv = os.path.join(flags.scene, 'frames.csv')
    with open(frames_csv, 'rt') as f:
        csv_reader = csv.reader(f)

        for line in csv_reader:
            if line[0] == 'timestamp':
                continue # header
            timestamp = line[0]
            frame = line[1]
            out[int(frame)] = float(timestamp)
    return out

def create_bag(flags, images):
    base_frame = 'base_frame'
    hand_frame = 'hand_frame'

    bag = rosbag.Bag(flags.out, 'w')
    bridge = CvBridge()
    frame_metadata = read_frame_metadata(flags)

    for i, image_path in enumerate(images):
        sys.stdout.write("\rPreprocessing image " + str(i))
        sys.stdout.flush()
        frame_number = image_path.split('.')[0]
        timestamp = frame_metadata[int(frame_number)]
        image = cv2.imread(os.path.join(flags.scene, 'color', image_path))
        msg = bridge.cv2_to_imgmsg(image, encoding='bgr8')
        msg.header.stamp = rospy.Time(secs=timestamp)
        print('image: ', timestamp)
        bag.write('/image', msg)

    with open(os.path.join(flags.scene, 'transforms.csv'), 'rt') as f:
        # transforms.csv contains: timestamp, source_frame, target_frame, x, y, z, qx, qy, qz, qw
        transform_reader = csv.DictReader(f)

        for line in transform_reader:
            tf_message = TFMessage()
            transform_stamped = TransformStamped()
            transform_stamped.transform.translation.x = float(line['x'])
            transform_stamped.transform.translation.y = float(line['y'])
            transform_stamped.transform.translation.z = float(line['z'])
            transform_stamped.transform.rotation.x = float(line['qx'])
            transform_stamped.transform.rotation.y = float(line['qy'])
            transform_stamped.transform.rotation.z = float(line['qz'])
            transform_stamped.transform.rotation.w = float(line['qw'])

            timestamp = float(line['timestamp'])
            print("tf: ", timestamp)
            transform_stamped.header.stamp = rospy.Time(secs=timestamp)
            transform_stamped.header.frame_id = line['source_frame']
            transform_stamped.child_frame_id = line['target_frame']
            tf_message.transforms = [transform_stamped]
            bag.write('/tf', tf_message)
    bag.close()
    print('')

def main():
    flags = read_args()

    color_path = os.path.join(flags.scene, 'color')
    color_images = os.listdir(color_path)
    color_images = [i for i in color_images if 'jpg' in i]
    color_images.sort()

    create_bag(flags, color_images)

if __name__ == "__main__":
    main()


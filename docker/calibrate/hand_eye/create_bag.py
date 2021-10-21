import os
import argparse
import sys
import rosbag
import rospy
import cv2
import numpy as np
import json
from tf import transformations
from geometry_msgs.msg import TransformStamped
from cv_bridge import CvBridge

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', required=True)
    parser.add_argument('--out', required=True)
    return parser.parse_args()

def read_trajectory(flags):
    poses = []
    trajectory_log = os.path.join(flags.scene, 'scene', 'trajectory.log')
    with open(trajectory_log, 'rt') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 5):
            rows = [np.fromstring(l, count=4, sep=' ') for l in lines[i+1:i+5]]
            poses.append(np.stack(rows))
    return poses

def create_bag(flags, dt, images):
    base_frame = 'base_frame'
    hand_frame = 'hand_frame'

    bag = rosbag.Bag(flags.out, 'w')
    bridge = CvBridge()
    trajectory = read_trajectory(flags)
    for i, image_path in enumerate(images):
        sys.stdout.write("\rPreprocessing image " + str(i))
        sys.stdout.flush()
        image = cv2.imread(os.path.join(flags.scene, 'color', image_path))
        msg = bridge.cv2_to_imgmsg(image, encoding='bgr8')
        timestamp = rospy.Time(secs=dt * i)
        msg.header.stamp =
        bag.write('/image', msg)

        T_CW = trajectory[i]

        transform_stamped = TransformStamped()
        t = T_CW[:3, 3]
        q = transformations.quaternion_from_matrix(T_CW)

        transform_stamped.transform.translation.x = t[0]
        transform_stamped.transform.translation.y = t[1]
        transform_stamped.transform.translation.z = t[2]
        transform_stamped.transform.rotation.x = q[0]
        transform_stamped.transform.rotation.y = q[1]
        transform_stamped.transform.rotation.z = q[2]
        transform_stamped.transform.rotation.w = q[3]

        transform_stamped.header.stamp = timestamp
        transform_stamped.header.frame_id = 'child_frame'
        transform_stamped.child_frame_id = 'hand_frame'
        bag.write('/tf', transform_stamped)
    print ''

def main():
    flags = read_args()

    camera_intrinsics = os.path.join(flags.scene, 'camera_intrinsics.json')
    with open(camera_intrinsics, 'rt') as f:
        camera_intrinsics = json.load(f)

    dt = 1.0 / camera_intrinsics['fps']

    color_path = os.path.join(flags.scene, 'color')
    color_images = os.listdir(color_path)
    color_images = [i for i in color_images if 'jpg' in i]
    color_images.sort()

    create_bag(flags, dt, color_images)

if __name__ == "__main__":
    main()


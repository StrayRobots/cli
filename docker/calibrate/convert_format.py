from __future__ import print_function
import argparse
import os
import csv
from time import time
from PIL import Image

DT = 1.0 / 60.0

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--out')
    return parser.parse_args()

def read_imu(flags):
    out = []
    imu_in_path = os.path.join(flags.scene, 'imu.csv')
    if os.path.exists(imu_in_path):
        with open(imu_in_path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                out.append(row)
    return out

def move_imu(flags, color_image):
    imu_path_out = os.path.join(flags.out, 'imu0.csv')
    imu_readings = read_imu(flags)
    with open(imu_path_out, 'wt') as f:
        writer = csv.writer(f)

        writer.writerow(['timestamp', 'omega_x', 'omega_y', 'omega_z', 'alpha_x','alpha_y', 'alpha_z'])
        if len(imu_readings) > 0:
            for reading in imu_readings:
                # bagcreater uses ts, rotation and then acceleration
                ts = str(int(float(reading[0]) * 1e9))
                writer.writerow([ts, reading[4], reading[5], reading[6], reading[1], reading[2], reading[3]])
        else:
            for color_image in color_images:
                num = os.path.basename(color_image).split('.')[0]
                ts = str(int(start + float(num) * DT * 1e9))
                writer.writerow([ts] + [0 for _ in range(6)])

def read_frames(flags, color_images):
    frames_path = os.path.join(flags.scene, 'frames.csv')
    timing = {}
    if not os.path.exists(frames_path):
        for color_image in color_images:
            num = os.path.basename(color_image).split('.')[0]
            ts = int(start + float(num) * DT * 1e9)
            timing[num] = ts
    else:
        with open(frames_path, 'rt') as f:
            reader = csv.reader(f)
            next(reader) # header
            for line in reader:
                timestamp = line[0]
                frame = line[1].strip()
                timing[frame] = str(int(float(timestamp) * 1e9))
    return timing

def main():
    flags = read_args()
    color_path = os.path.join(flags.scene, 'color')

    color_images = os.listdir(color_path)
    color_images = [i for i in color_images if 'jpg' in i]
    color_images.sort()

    try:
        os.makedirs(os.path.join(flags.out, 'cam0'))
    except OSError:
        pass

    start = time() * 1e9
    print("Creating dataset.")
    move_imu(flags, color_images)
    timing = read_frames(flags, color_images)

    for color_image in color_images:
        num = os.path.basename(color_image).split('.')[0]
        ts = timing[num]
        in_path = os.path.join(flags.scene, 'color', color_image)
        out_path = os.path.join(flags.out, 'cam0', ts + ".png")
        Image.open(in_path).save(out_path)
        print("Preprocessing image " + num)

if __name__ == "__main__":
    main()


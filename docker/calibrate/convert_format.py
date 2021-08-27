import argparse
import os
import csv
from time import time
from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('scene')
    parser.add_argument('--out')
    flags = parser.parse_args()

    color_path = os.path.join(flags.scene, 'color')
    imu_path = os.path.join(flags.out, 'imu0.csv')

    color_images = os.listdir(color_path)
    color_images = [i for i in color_images if 'jpg' in i]
    color_images.sort()

    dt = 1.0 / 60.0

    os.makedirs(os.path.join(flags.out, 'cam0'))

    start = time() * 1e9
    print("Creating dataset.")
    imu_readings = []
    imu_in_path = os.path.join(flags.scene, 'imu.csv')
    if os.path.exists():
        with open(imu_in_path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                imu_readings.append(row)

    with open(imu_path, 'wt') as f:
        writer = csv.writer(f)

        writer.writerow(['timestamp', 'omega_x', 'omega_y', 'omega_z', 'alpha_x','alpha_y', 'alpha_z'])
        if len(imu_readings) > 0:
            for reading in imu_readings:
                # bagcreater uses ts, rotation and then acceleration
                writer.writerow([reading[0], reading[4], reading[5], reading[6], reading[1], reading[2], reading[3]])
        else:
            for color_image in color_images:
                num = os.path.basename(color_image).split('.')[0]
                ts = str(int(start + float(num) * dt * 1e9))
                writer.writerow([ts] + [0 for _ in range(6)])

        for color_image in color_images:
            in_path = os.path.join(flags.scene, 'color', color_image)
            out_path = os.path.join(flags.out, 'cam0', ts + ".png")
            Image.open(in_path).save(out_path)
            print "Preprocessing image " + num

if __name__ == "__main__":
    main()


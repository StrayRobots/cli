from __future__ import print_function
import argparse
import os
import yaml

def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('imu_config')
    parser.add_argument('--out', required=True)
    return parser.parse_args()

def main():
    flags = read_args()

    with open(flags.imu_config, 'rt') as f:
        imu_config = yaml.load(f, Loader=yaml.SafeLoader)

    imu_config['ros_topic'] = '/imu0'

    with open(flags.out, 'wt') as f:
        f.write(yaml.dump(imu_config))

if __name__ == "__main__":
    main()


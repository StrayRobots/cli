#!/bin/bash

set -e

source $KALIBR_WORKSPACE/devel/setup.bash

mkdir -p /tmp/dataset
python3.8 /home/user/workspace/imu/create_bag.py --in-csv /home/user/workspace/data/imu.csv --out-csv /tmp/dataset/imu.csv


kalibr_bagcreater --folder /tmp/dataset/ --output-bag /tmp/bag.bag

roslaunch /home/user/workspace/imu/imu.launch &
sleep 5
rosbag play -r 100 /tmp/bag.bag > /dev/null

sleep 10

/bin/bash

mv /tmp/imu_out.yamliphone_imu_param.yaml /home/user/workspace/data/imu_config.yaml

rm -rf /tmp/dataset/ /tmp/bag.bag


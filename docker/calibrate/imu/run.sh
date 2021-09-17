#!/bin/bash

set -e

source $KALIBR_WORKSPACE/devel/setup.bash

mkdir -p /tmp/dataset
python /root/workspace/imu/create_bag.py --in-csv /root/workspace/data/imu.csv --out-csv /tmp/dataset/imu.csv


kalibr_bagcreater --folder /tmp/dataset/ --output-bag /tmp/bag.bag

roslaunch /root/workspace/imu/imu.launch &
sleep 5
rosbag play -r 100 /tmp/bag.bag > /dev/null

sleep 10

/bin/bash

mv /tmp/imu_out.yamliphone_imu_param.yaml /root/workspace/data/imu_config.yaml

rm -rf /tmp/dataset/ /tmp/bag.bag


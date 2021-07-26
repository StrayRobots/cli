#!/bin/bash

set -e
source /ros_entrypoint.sh

mkdir -p /root/workspace/data

python /root/workspace/convert_format.py /root/data/ --out /root/workspace/data

kalibr_bagcreater --folder /root/workspace/data --out /root/workspace/data/bag.bag
kalibr_calibrate_cameras --bag /root/workspace/data/bag.bag --target /root/workspace/target.yaml --topics /cam0/image_raw /cam0/image_raw --models pinhole-equi pinhole-equi
python /root/workspace/extract_calibration.py --calibration camchain-bag.yaml --out /root/data/camera_intrinsics.json

rm -rf /root/workspace/data


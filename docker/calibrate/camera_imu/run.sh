#!/bin/bash
set -e

python3.8 /home/user/workspace/convert_format.py /home/user/data/ --out /tmp/data
python3.8 /home/user/workspace/camera_imu/create_imu_config.py /home/user/workspace/imu.yaml --out /tmp/imu.yaml

kalibr_bagcreater --folder /tmp/data --out /tmp/data/bag.bag

cat /tmp/imu.yaml
kalibr_calibrate_imu_camera --bag /tmp/data/bag.bag --target /home/user/workspace/target.yaml --cam /home/user/workspace/camera.yaml --imu /tmp/imu.yaml --dont-show-report

mv camchain-imucam-tmpdatabag.yaml /home/user/data/camchain-imucam.yaml
mv results-imucam-tmpdatabag.txt /home/user/data/results-imucam.txt
mv report-imucam-tmpdatabag.pdf /home/user/data/report-imucam.pdf
mv imu-tmpdatabag.yaml /home/user/data/imu.yaml

rm -rf /tmp/data/


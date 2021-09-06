#!/bin/bash
set -e

python /root/workspace/convert_format.py /root/data/ --out /tmp/data
python /root/workspace/camera_imu/create_imu_config.py /root/workspace/imu.yaml --out /tmp/imu.yaml

kalibr_bagcreater --folder /tmp/data --out /tmp/data/bag.bag

kalibr_calibrate_imu_camera --bag /tmp/data/bag.bag --target /root/workspace/target.yaml --cam /root/workspace/camera.yaml --imu /tmp/imu.yaml --dont-show-report

mv camchain-imucam-tmpdatabag.yaml /root/data/camchain-imucam.yaml
mv results-imucam-tmpdatabag.txt /root/data/results-imucam.txt
mv report-imucam-tmpdatabag.pdf /root/data/report-imucam.pdf
mv imu-tmpdatabag.yaml /root/data/imu.yaml

rm -rf /tmp/data/


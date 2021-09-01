#!/bin/bash
set -e

python /root/workspace/convert_format.py /root/data/ --out /tmp/data

kalibr_bagcreater --folder /tmp/data --out /tmp/data/bag.bag

kalibr_calibrate_imu_camera --bag /tmp/data/bag.bag --target /root/workspace/target.yaml --cam /root/workspace/camera.yaml --imu /root/workspace/imu.yaml --dont-show-report

/bin/bash

mv camchain-imucam-tmpdatabag.yaml /root/data/camchain-imucam.yaml
mv results-imucam-tmpdatabag.txt /root/data/results-imucam.txt
mv report-imucam-tmpdatabag.pdf /root/data/report-imucam.pdf
mv imu-tmpdatabag.yaml /root/data/imu.yaml

rm -rf /tmp/data/


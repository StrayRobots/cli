#!/bin/bash

set -e

function src_ros() {
  # Avoids arguments getting passed in.
  source $KALIBR_WORKSPACE/devel/setup.bash
}
src_ros

if [ "$1" = "run" ]
then

  mkdir -p /root/workspace/data

  python /root/workspace/convert_format.py /root/data/ --out /root/workspace/data

  kalibr_bagcreater --folder /root/workspace/data --out /root/workspace/data/bag.bag
  kalibr_calibrate_cameras --bag /root/workspace/data/bag.bag --target /root/workspace/target.yaml --topics /cam0/image_raw --models pinhole-equi
  mv camchain-rootworkspacedatabag.yaml camchain-bag.yaml
  python /root/workspace/extract_calibration.py --calibration camchain-bag.yaml --out /root/data/camera_intrinsics.json

  mv report-cam-rootworkspacedatabag.pdf /root/data/calibration-report.pdf

  rm -rf /root/workspace/data
elif [ "$1" = "generate" ]
then
  shift
  pushd /root/data/
  python /root/workspace/create_target.py --target /root/workspace/target.yaml
  popd
else
  echo "Unrecognized command $1."
  exit 1
fi


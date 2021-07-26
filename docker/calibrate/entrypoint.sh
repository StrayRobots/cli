#!/bin/bash

set -e

function src_ros() {
  # Avoids arguments getting passed in.
  source /ros_entrypoint.sh
}
src_ros


if [ "$1" = "run" ]
then

  mkdir -p /root/workspace/data

  python /root/workspace/convert_format.py /root/data/ --out /root/workspace/data

  kalibr_bagcreater --folder /root/workspace/data --out /root/workspace/data/bag.bag
  kalibr_calibrate_cameras --bag /root/workspace/data/bag.bag --target /root/workspace/target.yaml --topics /cam0/image_raw /cam0/image_raw --models pinhole-equi pinhole-equi
  python /root/workspace/extract_calibration.py --calibration camchain-bag.yaml --out /root/data/camera_intrinsics.json

  rm -rf /root/workspace/data
elif [ "$1" = "generate" ]
then
  shift
  pushd /root/data/
  kalibr_create_target_pdf $@
  popd
else
  echo "Unrecognized command $1."
  exit 1
fi


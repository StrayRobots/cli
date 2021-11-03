#!/bin/bash

set -e

function src_ros() {
  # Avoids arguments getting passed in.
  source $KALIBR_WORKSPACE/devel/setup.bash
}
src_ros

intrinsics_calibration() {
  mkdir -p /home/user/workspace/data

  python3.8 /home/user/workspace/convert_format.py /home/user/data/ --out /home/user/workspace/data

  kalibr_bagcreater --folder /home/user/workspace/data --out /home/user/workspace/data/bag.bag

  kalibr_calibrate_cameras --bag /home/user/workspace/data/bag.bag --target /home/user/workspace/target.yaml --topics /cam0/image_raw --models pinhole-equi

  mv camchain-homeuserworkspacedatabag.yaml camchain-bag.yaml
  cp camchain-bag.yaml /home/user/data/camchain.yaml

  python3.8 /home/user/workspace/extract_calibration.py --calibration camchain-bag.yaml --out /home/user/data/camera_intrinsics.json

  mv report-cam-homeuserworkspacedatabag.pdf /home/user/data/calibration-report.pdf
  rm -rf /home/user/workspace/data
}

if [ "$1" = "run" ]
then
  task="$2"
  shift
  if [ "$task" = "intrinsics" ]
  then
    echo "Calibrating camera intrinsics."
    intrinsics_calibration $@
  elif [ "$task" = "imu_noise" ]
  then
    echo "Calibrating imu noise."
    /home/user/workspace/imu/run.sh $@
  elif [ "$task" = "camera_imu" ]
  then
    echo "Calibrating camera to imu."
    /home/user/workspace/camera_imu/run.sh $@
  elif [ "$task" = "hand_eye" ]
  then
    echo "Running hand-eye calibration."
    /home/user/workspace/hand_eye/run.sh $@
  else
    echo "Unrecognized calibration task $task."
    exit 1
  fi
elif [ "$1" = "generate" ]
then
  shift
  pushd /home/user/data/
  python3.8 /home/user/workspace/create_target.py --target /home/user/workspace/target.yaml
  popd
else
  echo "Unrecognized command $1."
  exit 1
fi


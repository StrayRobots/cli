#!/bin/bash

set -e

function src_ros() {
  # Avoids arguments getting passed in.
  source $KALIBR_WORKSPACE/devel/setup.bash
}
src_ros


calibrate_cameras() {
  python /root/workspace/convert_format.py /root/data/ --out /root/workspace/data

  kalibr_bagcreater --folder /root/workspace/data --out /root/workspace/data/bag.bag

  kalibr_calibrate_cameras --bag /root/workspace/data/bag.bag --target /root/workspace/target.yaml --topics /cam0/image_raw --models pinhole-equi

  mv camchain-rootworkspacedatabag.yaml camchain-bag.yaml
  cp camchain-bag.yaml /root/data/camchain.yaml

  python /root/workspace/extract_calibration.py --calibration camchain-bag.yaml --out /root/data/camera_intrinsics.json

  mv report-cam-rootworkspacedatabag.pdf /root/data/calibration-report.pdf
}

if [ "$1" = "run" ]
then

  mkdir -p /root/workspace/data

  args=("$@")
  # Defaults to camera intrinsics calibration
  # if --imu-noise is specified, it will assume the imu.csv file contains at least an hour
  # of imu data where the device was static and not moving.
  # --camera-imu is for calibrating camera to imu.
  imu_noise_calibration=false
  camera_imu_calibration=false
  echo "Calibration run $@"
  for arg in "$@"
  do
    if [ "${args[i]}" = "--imu-noise" ]
    then
      imu_noise_calibration=true
    elif [ "${args[i]}" = "--camera-imu" ]
    then
      camera_imu_calibration=true
    fi
    i=$((i + 1))
  done

  if [ "$imu_noise_calibration" = true ]
  then
    echo "Calibrating imu noise"
    /root/workspace/imu/run.sh $@
  elif [ "$camera_imu_calibration" = true ]
  then
    echo "Calibrating camera to imu"
    /root/workspace/camera_imu/run.sh $@
  else
    calibrate_cameras $@
  fi

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


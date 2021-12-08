#!/bin/bash

set -e

python3.8 validate_license.py

orbslam_settings_path=/tmp/orbslam_settings.yaml

skip_slam=0

image_count=$(ls -1 $1 | wc -l)
if (( $image_count < 50 )); then
  skip_slam=1
fi

i=0
args=("$@")
every=60
for arg in "$@"
do
    if [ "${args[i]}" = "--no-slam" ]
    then
      skip_slam=1
    elif [ "${args[i]}" = "--no-slam" ]
    then
      every="${args[i+1]}"
    fi
    i=$((i + 1))
done

if [ "$skip_slam" = "1" ]; then
  every=1
fi

python3.8 filter_images.py $1 --every $every
pushd Meshroom-2021.1.0-av2.4.0-centos7-cuda10.2 > /dev/null
./meshroom_batch -i $1/filtered_color --cache $1/MeshroomCache
rm -rf $1/filtered_color
popd > /dev/null

python3.8 /home/user/workspace/prepare_scene.py $1
python3.8 /home/user/workspace/make_settings.py $1 --default-settings /home/user/workspace/default_settings.yaml -o $orbslam_settings_path
pushd /home/user/orbslam/Examples/RGB-D > /dev/null


if [ "$skip_slam" = "0" ]
then
  ./rgb ../../Vocabulary/ORBvoc.txt $orbslam_settings_path $1 1.0
  mv CameraTrajectory.txt $1/CameraTrajectory.txt
fi

popd > /dev/null
python3.8 /home/user/workspace/combine_trajectories.py $1
rm -rf $1/CameraTrajectory.txt
rm -rf $1/MeshroomCache


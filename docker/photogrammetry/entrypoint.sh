#!/bin/bash

set -e

python3.8 validate_license.py

python3.8 filter_images.py $1
pushd Meshroom-2021.1.0-av2.4.0-centos7-cuda10.2 > /dev/null
./meshroom_batch -i $1/filtered_color --cache $1/MeshroomCache
rm -rf $1/filtered_color
popd
python3.8 /home/user/workspace/prepare_scene.py $1
python3.8 /home/user/workspace/make_settings.py $1 --default-settings /home/user/workspace/default_settings.yaml -o $1/orbslam_settings.yaml
pushd /home/user/orbslam/Examples/RGB-D > /dev/null 
./rgb ../../Vocabulary/ORBvoc.txt $1/orbslam_settings.yaml $1 0.1
mv CameraTrajectory.txt $1/CameraTrajectory.txt
popd
python3.8 /home/user/workspace/combine_trajectories.py $1
rm -rf $1/CameraTrajectory.txt
rm -rf $1/MeshroomCache
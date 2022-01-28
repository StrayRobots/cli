#!/bin/bash

set -e

# python3.8 validate_license.py

pushd Meshroom-2021.1.0-av2.4.0-centos7-cuda10.2 > /dev/null

python3.8 /home/user/workspace/create_sfm.py $1 --out /tmp/cameras.sfm

./meshroom_batch --cache $1/MeshroomCache -i /tmp/cameras.sfm -p /home/user/workspace/pipeline.mg

popd > /dev/null

python3.8 /home/user/workspace/combine_trajectories.py $1
python3.8 /home/user/workspace/integrate.py $1 --voxel-size 0.01
python3.8 /home/user/workspace/integrate_pointcloud.py $1 --voxel-size 0.01
rm -rf $1/MeshroomCache


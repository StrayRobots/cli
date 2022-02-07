#!/bin/bash

set -e

# python3.8 validate_license.py

args=("$@")
debug=0
for arg in "$@"
do
    if [ "${args[i]}" = "--debug" ]
    then
        debug=1
    fi
    i=$((i + 1))
done

if [ "$debug" = "1" ];
then
  python3.8 /home/user/workspace/run_sfm.py /home/user/data --debug
  python3.8 /home/user/workspace/combine_trajectories.py $1 --colmap-dir "/home/user/data/sfm/sfm/0"
else
  python3.8 /home/user/workspace/run_sfm.py /home/user/data
  python3.8 /home/user/workspace/combine_trajectories.py $1 --colmap-dir "/tmp/sfm/sfm/0"
fi

python3.8 /home/user/workspace/integrate.py $1 --voxel-size 0.01
python3.8 /home/user/workspace/integrate_pointcloud.py $1 --voxel-size 0.01
rm -rf $1/MeshroomCache


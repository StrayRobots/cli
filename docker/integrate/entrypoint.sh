#!/bin/bash

set -e

debug=0
skip_mapping=0
voxel_size=0.01

args=("$@")
for arg in "$@"; do
  if [ "${args[i]}" = "--debug" ]
  then
    debug=1
  elif [ "${args[i]}" = "--skip-mapping" ]
  then
    skip_mapping=1
  elif [ "${args[i]}" = "--voxel-size" ]
  then
    voxel_size="${args[i+1]}"
  fi
  i=$((i + 1))
done

integrate_scene() {
  if [ "$skip_mapping" = "0" ];
  then
    if [ "$debug" = "1" ];
    then
      python3.8 /home/user/workspace/run_sfm.py $1 --debug
      python3.8 /home/user/workspace/combine_trajectories.py $1 --colmap-dir "/home/user/data/sfm/sfm/0"
    else
      python3.8 /home/user/workspace/run_sfm.py $1
      python3.8 /home/user/workspace/combine_trajectories.py $1 --colmap-dir "/tmp/sfm/sfm/0"
    fi
  fi
  python3.8 /home/user/workspace/integrate.py $1 --voxel-size $voxel_size
  python3.8 /home/user/workspace/integrate_pointcloud.py $1 --voxel-size $voxel_size
}

if [ -f "/home/user/data/camera_intrinsics.json" ];
then
  integrate_scene /home/user/data
else
  # An entire dataset was given. Integrate each scene.
  for dir in $1/*; do
    echo "Integrating scene $(basename $dir)"
    integrate_scene $dir
  done
fi



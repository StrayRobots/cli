#!/bin/bash

# Usage: <image> <path-to-scenes>

set -e

for d in "/home/user/data/"*; do
    if [ -d $d ]
        then
        if [ -d "$d/scene" ]
        then
            echo "Directory $d/scene exists, skipping."
        else
            echo "Computing trajectory for scene $d"

            python3 /home/user/workspace/make_settings.py $d --default-settings /home/user/workspace/default_settings.yaml -o /home/user/workspace/settings.yaml

            pushd /home/user/orbslam/Examples/RGB-D > /dev/null

            ./o3d ../../Vocabulary/ORBvoc.txt /home/user/workspace/settings.yaml $d

            echo "Integrating scene."

            python3 /home/user/workspace/integrate.py $d --trajectory CameraTrajectory.txt

            echo "Integrating point cloud."

            python3 /home/user/workspace/integrate_pointcloud.py $d

            popd > /dev/null
        fi
    fi
done

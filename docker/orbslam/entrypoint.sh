#!/bin/bash

# Usage: <image> <path-to-scenes>

set -e

integrate_scene() {
    python3 /home/user/workspace/make_settings.py $1 --default-settings /home/user/workspace/default_settings.yaml -o /home/user/workspace/settings.yaml

    pushd /home/user/orbslam/Examples/RGB-D > /dev/null

    ./o3d ../../Vocabulary/ORBvoc.txt /home/user/workspace/settings.yaml $1

    echo "Integrating scene."

    python3 /home/user/workspace/integrate.py $1 --trajectory CameraTrajectory.txt

    echo "Integrating point cloud."

    python3 /home/user/workspace/integrate_pointcloud.py $1

    popd > /dev/null
}

if [ -d "/home/user/data/color" ]
then
    echo "Computing trajectory for scene."
    integrate_scene "/home/user/data/"
else
    for d in "/home/user/data/"*; do
        if [ -d $d ]
            then
            if [ -d "$d/scene" ]
            then
                echo "Directory $(basename $d)/scene exists, skipping."
            else
                echo "Computing trajectory for scene $(basename $1)"

                integrate_scene $d
            fi
        fi
    done
fi


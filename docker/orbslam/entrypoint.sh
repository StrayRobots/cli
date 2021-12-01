#!/bin/bash

# Usage: <image> <path-to-scenes>

set -e

python3.8 validate_license.py

validate_scene() {
    if [ ! -d "$1/color" ] || [ ! -d "$1/depth" ] || [ ! -f "$1/camera_intrinsics.json" ]
    then
        echo "$(basename $1) does not look like a scene path."
        exit 1
    fi
}

slam_step() {
    i=0
    args=("$@")
    sleep=1
    debug=0
    for arg in "$@"
    do
        if [ "${args[i]}" = "--settings" ]
        then
            settings=${args[i+1]}
        fi
        if [ "${args[i]}" = "--sleep" ]
        then
            sleep=${args[i+1]}
        fi
        if [ "${args[i]}" = "--debug" ]
        then
            debug=1
        fi
        i=$((i + 1))
    done

    if [ -n "$settings" ]
    then
        echo "Overriding SLAM settings"
        python3.8 /home/user/workspace/make_settings.py $1 --default-settings /home/user/workspace/default_settings.yaml \
            --settings $settings \
            -o /home/user/workspace/settings.yaml
    else
        python3.8 /home/user/workspace/make_settings.py $1 --default-settings /home/user/workspace/default_settings.yaml \
            -o /home/user/workspace/settings.yaml
    fi

    pushd /home/user/orbslam/Examples/RGB-D > /dev/null

    if [ $debug = 1 ]
    then
        ./o3d ../../Vocabulary/ORBvoc.txt /home/user/workspace/settings.yaml $1 $sleep --debug
    else
        ./o3d ../../Vocabulary/ORBvoc.txt /home/user/workspace/settings.yaml $1 $sleep
    fi

    popd > /dev/null
}

integrate_scene() {
    validate_scene $1

    if [ -f "$1/scene/trajectory.log" ]
    then
        echo "Scene already has trajectory. Skipping SLAM step."
    else
        slam_step $@
    fi

    echo "Integrating scene."

    i=0
    args=("$@")
    voxel_size="0.005"
    for arg in "$@"
    do
        if [ "${args[i]}" = "--voxel-size" ]
        then
            voxel_size=${args[i+1]}
        fi
        i=$((i + 1))
    done

    python3.8 /home/user/workspace/integrate.py $1 --trajectory CameraTrajectory.txt --voxel-size $voxel_size

    echo "Integrating point cloud."

    python3.8 /home/user/workspace/integrate_pointcloud.py $1
}

success=0

if [ -d "/home/user/data/color" ] && [ -f "/home/user/data/camera_intrinsics.json" ]
then
    echo "Computing trajectory for scene."
    integrate_scene "/home/user/data/" $@
    success=1
else
    for d in "/home/user/data/"*; do
        if [ -d $d ]
            then
            if [ -f "$d/scene/integrated.ply" ]
            then
                echo "Mesh $(basename $d)/scene/integrated.ply exists, skipping."
            else
                echo "Computing trajectory for scene $(basename $1)"
                integrate_scene $d $@
            fi
            success=1
        fi
    done
fi

if [ "$success" = "0" ]
then
    echo "Doesn't look like a scene folder. Check your scene path arguments."
fi


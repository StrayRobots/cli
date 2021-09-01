#!/bin/bash

# Usage: <image> <path-to-scenes>

set -e

integrate_scene() {
    i=$((i + 1))
    args=("$@")
    echo "args: $@"
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
    echo "Settings $settings"
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

    echo "Integrating scene."

    python3.8 /home/user/workspace/integrate.py $1 --trajectory CameraTrajectory.txt

    echo "Integrating point cloud."

    python3.8 /home/user/workspace/integrate_pointcloud.py $1

    popd > /dev/null
}

if [ -d "/home/user/data/color" ]
then
    echo "Computing trajectory for scene."
    integrate_scene "/home/user/data/" $@
else
    for d in "/home/user/data/"*; do
        if [ -d $d ]
            then
            if [ -d "$d/scene" ]
            then
                echo "Directory $(basename $d)/scene exists, skipping."
            else
                echo "Computing trajectory for scene $(basename $1)"
                integrate_scene $d $@
            fi
        fi
    done
fi


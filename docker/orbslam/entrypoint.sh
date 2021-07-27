#!/bin/bash

# Usage: <image> <path-to-scene>

set -e

echo "Computing trajectory"

python3 /root/workspace/make_settings.py /root/data/ --default-settings /root/workspace/default_settings.yaml -o /root/workspace/settings.yaml

pushd /root/orbslam/Examples/RGB-D

./o3d ../../Vocabulary/ORBvoc.txt /root/workspace/settings.yaml /root/data/

echo "Integrating."

python3 /root/workspace/integrate.py /root/data/ --trajectory CameraTrajectory.txt

popd


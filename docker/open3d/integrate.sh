#!/bin/bash

set -e

echo "Integrating scene $1"

ls /root/dataset/

python3 /root/workspace/create_config.py /root/dataset/ /root/workspace/config.json

pushd /root/open3d/examples/python/reconstruction_system/

python3 run_system.py /root/workspace/config.json --make --register --refine --integrate --slac --slac_integrate

popd


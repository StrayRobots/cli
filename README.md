# Stray CLI

Stray CLI is a tool for working with RGB-D datasets. It can import scans from [Stray Scanner](https://apps.apple.com/us/app/stray-scanner/id1557051662) through the `stray import` command, compute camera poses and global point clouds using the `stray integrate` command and export datasets for object detection.

## Mapping pipeline

![Fire hydrant point cloud scanned with Stray Scanner](assets/images/fire_hydrant.jpg).

The [`stray integrate`](https://docs.strayrobots.io/commands/integrate.html) can be used to compute camera poses for RGB-D scans and compute a point cloud and mesh of the scene. Check the documentation for more details.

Scenes that were collected using Stray Scanner can be imported and integrated using the following commands:
```
mkdir dataset
stray import <stray-scanner-scene> --out dataset/ # import the scene into newly created folder
stray integrate dataset/<scene-name> # Integrate the scene
stray studio dataset/<scene-name> # Open the scene in Stray Studio
```

## Installing

The mapping pipeline relies on [Nvidia docker](https://github.com/NVIDIA/nvidia-docker) to run and requires a CUDA 11 capable GPU. Make sure to install Nvidia Docker and Docker first, by following the instructions [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker).

To make use of the import and other commands that make use of Python, you will have to install the stray Python package into your currently active Python environment. You can do this by running `pip install stray`.

If you are running and x86 macOS or Linux system, you can install the tool along with [Stray Studio](https://github.com/StrayRobots/3d-annotation-tool) by running the `./bin/install_local.sh` script. This will install the toolkit into `$HOME/.stray` and download the Stray Studio binaries in there as well. It will also add the stray command into your `.bashrc` or `.zshrc` file.

ARM and Apple M systems are currently not supported, though PRs adding support are welcome.

## Documentation

Documentation is hosted [here](https://docs.strayrobots.io). The documentation is built based on the mdbook files located under the `docs` subdirectory.


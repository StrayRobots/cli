# Integrate

Usage: `stray integrate <scenes-directory> [--skip-mapping]`

The integrate command is an offline mapping pipeline which takes color and depth images in the scene along with odometry information to compute poses for each image. Additionally, it will compute a global point cloud and mesh of the scene.

Inputs:
- Color images from `color`
- Depth images from `depth`
- Odometry from `frames.csv`

Outputs:
- Scene point cloud at `scene/cloud.ply`
- Scene mesh at `scene/integrated.ply`
- Camera trajectory at `scene/trajectory.log`

The scene directory follows the [scene format](/formats/data.md#dataset-format).

Under the hood, the pipeline uses [hloc](https://github.com/cvg/Hierarchical-Localization) on a subset of the images to compute optimized camera poses, which are then combined with the odometry data to compute a camera pose for every frame.

## Example

In case you just want to test the pipeline, you can download the example scene , run the pipeline and open it in studio with the following commands:
```
wget https://stray-data.nyc3.digitaloceanspaces.com/datasets/scooter.tar.gz -O scooter.tar.gz
tar -xvf scooter.tar.gz
stray integrate scooter/
stray studio scooter/
```

## Using known camera poses

In case you already have known camera poses, as might be the case for example when using a camera mounted on a robot arm which is calibrated, you can skip the mapping part with the `--skip-mapping` to simply integrate the RGB-D frames into a point cloud and mesh using the poses in `frames.csv`.


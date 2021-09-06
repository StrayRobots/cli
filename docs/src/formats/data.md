# Dataset Format

Stray operates on a standard dataset format. A dataset consists of one or more **scenes** stored in a directory. A dataset directory consists of several scene directories.

## Scene Format

Each **scene** directory should contain:
### `color`

Contains numbered (`000.jpg`, `001.jpg`, ..) color images (jpg/png) of the image sequence used to produce the scene

### `depth`
Contains numbered (`000.png`, `001.png`, ...) png files which contain depth maps used to produce the scene.

Depth maps are encoded as 16 bit grayscale png images, where each value corresponds to depth in millimeters.

### `camera_intrinsic.json`
Contains the intrinsic parameters of the camera that was used to collect the `color` and `depth` files.
It should contain a single object, with the following fields:
  - `depth_format` **string**, the data format of depth frames, currently only `Z16` is supported, meaning 16-bit grayscale
  - `depth_scale` **number**, the depth scale of the depth maps. The depth value divided this value should equal the depth in meters.
  - `fps` **number**, the frame rate (fps) used to collect the `color` and `depth` files
  - `width` **number**, width of the `color` and `depth` files
  - `height` **number**, height of the `color` and `depth` files
  - `intrinsic_matrix` **array** of **number**s, the intrinsic matrix of the camera used to collect the `color` and `depth` files. Details about the intrinsic matric can be found for example on [Wikipedia](https://en.wikipedia.org/wiki/Camera_matrix)
  - `camera_model` **string**, should be `pinhole` for now.
  - `distortion_model` **string** (optional) currently, only `KannalaBrandt` is supported.
  - `distortion_coefficients` **list of 4 floats**, these are the distortion coefficients for the camera model. See [camera calibration]() for details on how to obtain these.

Here is an example of a `camera_intrinsics.json` file:
```
{
    "depth_format": "Z16",
    "depth_scale": 1000.0,
    "fps": 60.0,
    "height": 480,
    "width": 640,
    "intrinsic_matrix": [
        483.9207283436,
        0.0,
        0.0,
        0.0,
        484.2223165574,
        0.0,
        308.8264255133,
        240.4719135967,
        1.0
    ],
    "camera_model": "pinhole",
    "distortion_model": "KannalaBrandt",
    "distortion_coefficients": [0.4930586782521112, -0.42050294868589483, 1.2586663628718142, -1.1575906751296825]
}
```

In addition, the following data can be created with various Stray [commands](/commands/index.md):
### `scene`
    - Contains a mesh file called `integrated.ply`
    - Contains a camera pose trajectory file called `trajectory.log`
    - Can be created with the `stray studio integrate` [command](/commands/studio.md#stray-studio-integrate)

### `annotations.json`
A json file created by [Studio](/commands/studio.md#stray-studio-open) which contains annotations (keypoints, bounding boxes etc.) that have been added to the scene.

Here is an example `annotations.json` file:
```
{
  "bounding_boxes":[{
    "instance_id": 0,
    "dimensions": [0.07500000298023224, 0.07500000298023224, 0.2919999957084656],
    "orientation": {"w": -0.36170855164527893, "x": 0.30457407236099243, "y": 0.8716252446174622, "z": -0.12911593914031982},
    "position": [-0.030162816867232323, 0.02697429060935974, 0.5071253776550293]
  }],
  "keypoints":[{
    "instance_id": 0,
    "position": [-0.1353698968887329, 0.027062859386205673, 0.413930207490921]
  }]
}
```

- `bounding_boxes` are the bounding boxes that have been placed in the scene.
  - `instance_id` is the numerical id of the object class.
  - `dimensions` is the size of the bounding box in meters along the x, y and z directions in the local coordinate frame of the bounding box.
  - `orientation` w, x, y, z are components of a quaternion that rotate the bounding box from world to object coordinates.
  - `position` is the translation from world to the center of the bounding box.
- `keypoints` are individual keypoints that have been placed with the keypoint tool. They are points and have a position, but no rotation.
  - `instance_id` is the numerical id of the keypoint type.
  - `position` is the position of the keypoint in the scene's coordinate frame.


### `<primitive>_labels`
Directories containing labels (semantic masks, keypoint annotations etc.) that can be created with the `stray label generate` [command](/commands/label.md#stray-label-generate)

Available `primitive` types are:
- `semantic`, semantic segmentation masks saved as png files
- `bbox_3d`, 3D bounding boxes saved as csv
- `bbox_2d`, 2D bounding boxes saved as csv
- `keypoints`, 3D keypoints saved as csv

## Scene Configuration

In addition to scene folders, a dataset directory can contain a `metadata.json` file which details how many object classes there are and what these correspond to. You can also specify the size of each object type, which speeds up labeling and reduces errors.

A `metadata.json` file should contain a single object with the following fields:
- `num_classes` **integer** -- how many different classes are in the dataset
- `instances` **list of instance objects**
    - An **instance object** contains the following fields:
        - `instance_id` **positive integer** these should start from 0 and increase
        - `name` **string** the name of the class
        - `size` **array with 3 float values** extents of the object in meters in the **x**, **y** and **z** directions which is used as the default bounding box size

Here is an example configuration.
```
{
  "num_classes": 2,
  "instances": [{
    "instance_id": 0,
    "name": "Wine Bottle",
    "size": [0.075, 0.075, 0.292]
  }, {
    "instance_id": 1,
    "name": "33cl Can",
    "size": [0.066, 0.066, 0.115]
  }]
}
```
## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.


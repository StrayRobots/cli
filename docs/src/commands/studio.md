# Studio

The `studio` subcommand is used to integrate scenes from [datasets](/formats/data.md) and provides a visual interface to annotate the scene.

![Stray Studio Interface](/images/studio.jpg)

## Available commands

## `stray studio integrate <scenes-directory>`

Reads color and depth images from a scene to compute the trajectory of the camera and produces a mesh of the scene. After this has been done, the scene can be opened in the Studio with the open command.

The scene directory has to follow the [dataset format](/formats/data.md#dataset-format).

#### Options

|name|default|choices|description|
|---|---|---|---|
|`scenes`| | |Path to the directory containing the [scenes](/formats/data.md#dataset-format) to integrate|
|`--voxel-size`| 0.01 (meters) | | Sets the grid size used when creating the mesh and point cloud of a scene. This can be roughly interpreted as the finest level of detail that will be distinguishable in the scene. The smaller the value, the more memory will be required and the longer the command will take.|
|`--skip-mapping`| false | | If this is set, no image matching, mapping and bundle adjustment is performed and the poses in `scene/trajectory.log` are assumed to be perfect.|

## `stray studio open <scene>`

Opens a scene in the Studio graphical user interface. Before a scene can be opened, it has to be integrated with the [`integrate`](#stray-studio-integrate-scene-directory) command.

## `stray studio preview <scene>`

Plays through images in the scene with overlayed 3d annotations.

#### Options

|name|default|choices|description|
|---|---|---|---|
|`scene`| | |Path to a single [scene](/formats/data.md#dataset-format) to open|

#### Keyboard Shortcuts for Stray Studio

`cmd+s` to save.

`k` switches to the keypoint tool.

`v` switches to the move tool.

`b` switches to the bounding box tool.

`r` switches to the rectangle tool.

`shift+1` switches to the mesh view.

`shift+2` switches to the point cloud view.


## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.


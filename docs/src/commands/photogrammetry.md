# The Photogrammetry command

The `photogrammetry` command is an alternative to the `stray studio integrate` command for cases where you only have RGB images.

As of now, the photogrammetry pipeline does not provided scaled meshes. In fact, this is not possible to do from images alone and another source of information has to be added for scale. If you have a use case that requires the data to be in metric scale and only have color images, contact us.

Some best practices for using this command:
- Use images with at least full hd quality (1920x1080), the higher the better
- Have at least 25 different images taken from different viewpoints
- Make sure that all surfaces you need to reconstruct are clearly visible from two or more different viewpoints
- Avoid motion blur and make sure images are well exposed

## Available commands
## `stray photogrammetry run <scene-directory>`

Runs the photogrammetry pipeline and generates the `scene` folder that can be opened by the [studio command](/commands/studio.md).

#### Options

The command will run both photogrammetry to reconstruct the scene. By default, photogrammetry is only run on a subset of images, or all if there are fewer than 50 images. In case there are a lot of images, it will additionally run simultaneous localization and mapping (SLAM) to get camera poses for all the images, as running photogrammetry on lots of images quickly becomes infeasible. Also, running it on poses that a very near each other doesn't help that much.

|name|default|choices|description|
|---|---|---|---|
|`scene`| None - required | | The [scene](/formats/data.md#scene-format) to integrate. |
|`--skip-slam`|off||Only runs photogrammetry and skips running the SLAM step.|



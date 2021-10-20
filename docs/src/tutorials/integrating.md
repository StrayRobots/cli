# Tutorial: Integrating a scene for 3D labeling

First, make sure you have the Stray Toolkit installed and that you have imported a scene. If you haven't, check out the [importing tutorial](/tutorials/importing.md).

To proceed, you will need a dataset with at least one scene. An example directory structure might look like this:
```
dataset/
    scene1/
    scene2/
```
Where `scene1` and `scene2` are scenes following the [scene dataset format](/formats/data.md).

Check that the Stray Toolkit is installed and loaded in your shell with `stray --version`. This should print something similar to `Stray Robots CLI version 1.0.0`.

If not, check out the [installation guide](/installation/index.md).

## Integrating the scene

Scenes are integrated with the `stray studio integrate` command.

With the above directory structure, we run:
```
stray studio integrate dataset/scene1
```
to integrate `scene1`.

## Checking the results

To check the result of the integration run `stray studio open dataset/scene1`.

![Studio Electric Scooter](/images/tutorials/studio_example.webp)

That's it! Now you can start creating entire datasets and adding your annotations using Studio.



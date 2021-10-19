# Tutorial: Recording and importing data from Stray Scanner

In this tutorial, we cover how to import data from the [Stray Scanner app](https://apps.apple.com/us/app/stray-scanner/id1557051662) into the Stray Command Line Tool and Stray Studio.

To walk through this tutorial, you will need:
1. A LiDAR enabled iOS device, such as an iPhone 12 Pro, an iPhone 13 Pro or an iPad Pro with a LiDAR sensor
2. The Stray Scanner app installed on the device
3. A computer with the [Stray CLI](/installation/index.md) installed

While this tutorial covers the Stray Scanner app, you can import data from any other depth sensor. [Here](https://github.com/StrayRobots/StrayPublic/tree/main/realsense) is an example on how to record data using an Intel RealSense sensor.

The goal of this tutorial is to scan a scene using a depth sensor and convert it into a dataset that follows [our scene and dataset format](/formats/data.md). If you have some other depth sensor  you can [reach out to us](mailto:hello@strayrobots.io?subject=Sensor%20Support) and we can hopefully add support for your depth sensor. If you are dealing with some other dataset format that you would like to import, you can always write your own data format conversion script.

## Recording a scene using Stray Scanner

First, we need to record a scene to process. This is done by opening app, tapping "Record a new session", then press the red button to start a recording. Then scan the scene by filming a short clip that views the relevant parts of the scene from different viewpoints.

**Pro tip**: you can tap on the video view to switch between depth and rgb mode.

Some suggestions to get the best possible results:
- Make sure to avoid shaking and fast motion
    - Blurred images will make it hard for the reconstruction pipeline to localize the frames
- Keep clips short and to the point
    - The more frames in the clips, the longer it will take to process
- Make sure that recognizable features are visible in every frame
    - Avoid recording close to featureless objects such as walls
    - If no features are visible or the view is covered, the software might not be able to localize the camera
- Observe the scanning target from multiple viewpoints
    - This ensures that the target can be properly reconstructed in the integration step


## Moving the data over to your computer

Now that we have a scene recorded, we can move it over to our computer.

Here, we use a macOS computer with Finder. If you are on Linux, use the iOS Files app to access the Stray Scanner folder and move it over through a cloud service or share it through some other app.

First, we create two folders: a dataset folder which will contain our processed imported scenes and a staging folder where we temporarily keep the Stray Scanner scans. To create these, we run:
```
mkdir dataset/
mkdir staging/
```

To move the files over to the staging folder:
1. Connect your iPhone or iPad to your computer using a Lightning cable
2. Open Finder.app
3. Select your device from the sidebar
4. Click on the "Files" tab beneath your device description
5. Under "Stray Scanner", you should see one directory per scene you have collected. Drag the scanned folders to the `staging` folder

![How to access Stray Scanner data](/images/euclid.jpg)

---
**Note:**
The directories are named using random hashes, for example "ac1ed2228f". This is to prevent conflicts with scenes collected using other devices, when you are collaborating with other people. This avoids having to rename them later, though we do agree that it can sometimes be hard to keep track of which scene is which. Feel free to rename the rename the folders however you like.

---

Now that  we have moved over the scenes, we can import and convert them to our data format and into our dataset. This is done with the `stray dataset import` command:
```
stray dataset import staging/* --out dataset/
```

Optionally, you can specify the resolution at which you want to import the dataset by appending `--width=<width> --height=<height>` to the command. For example, `stray dataset import staging/* --out dataset --width=1920 --height=1440`. Generally, we recommend a larger resolution, but sometimes, smaller can be easier to work with and can be good enough quality wise.

To verify that the dataset was imported correctly, you can play through the image frames with the `stray dataset show dataset/*` command. This will play through the scenes one image at the time.

## Concluding

Now we have successfully imported our first scene! Now it's time to move on to the next step, which is [integrating your scenes](/tutorials/integrating.md). The integration step, takes a scene, recovers camera poses and creates a 3D reconstruction of the scene. This allows us to label the scenes in 3D.


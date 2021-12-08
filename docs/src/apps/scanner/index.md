![Stray Toolkit](/images/stray-logo.png)
# Stray Scanner

Stray Scanner is an iOS app for collecting RGB-D datasets. It can be downloaded from the [App Store](https://apps.apple.com/us/app/stray-scanner/id1557051662).

The recorded datasets contain:
- color images
- depth frames from the LiDAR sensor
- depth confidence maps
- camera position estimates for each frame
- camera calibration matrix
- IMU measurements

They can be converted into our scene [data format](/formats/data.md) with the [`stray dataset import`](/commands/dataset.md) command.


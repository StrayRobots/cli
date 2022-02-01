
# Export

This command can be used to export datasets from the Stray dataset format to other formats.

## Exporting as a YOLO dataset

[Yolo](https://pjreddie.com/darknet/yolo/) is a common network used for 2d bounding box detection.

The following command will export in yolo format:
```
stray export --train <training-dataset> --val <validation-dataset> --out <desired-output-path>
```

#### Options

|name|default|required|description|
|---|---|---|---|
|`--train`| | yes | The dataset to use as training. |
|`--val`| | yes | The dataset to use as a validation set.|
|`--out` | | yes | Where to create the exported dataset. |
|`--use-corners` | False | no | Use 3D bounding box corners to compute the 2D bounding boxes, instead of 3D geometry. |


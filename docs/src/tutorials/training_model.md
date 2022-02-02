# Training a model

Once we have collected and annotated a dataset, the next natural step is often to train a model to predict the labels.

In this tutorial, we are going to show you how to export your dataset and train a YOLO object detector on your dataset.

We assume that you have a dataset in Stray format that is organized as follows:
```
dataset/
  - scene1
  - scene2
  - scene3
  - ...
```

## Exporting data

The first step, is to split your dataset into two different parts. A training set, and a separate disjoint validation set. The validation set is used to check that your model is able to generalize to unseen examples.

Create two different directories, one for your training set and one for your test set.
```
mkdir train && mkdir validation
```

Then move part of your scenes into the validation set. For example, 10% can be a good starting point. Place the rest of your scenes into the training set.

Your directory structure should look something like this:
```
train/
  - scene1
  - scene2
  - ...
validation/
  - scene3
  - ...
```

Now export with the command:
```
stray export --train train --validation validation --out yolo_dataset
```

The `yolo_dataset` directory will contain a dataset in the yolo format that can be used in training a model.

## Training YOLO

Here, we will use the [YOLOv5 project](https://github.com/ultralytics/yolov5). Check the project for more detailed instructions.

To download and install it:
```
git clone https://github.com/ultralytics/yolov5/
cd yolov5
pip install -r requirements.txt
python train.py --img 640 --batch 16 --epochs 10 --data yolo_dataset/dataset.yaml --weights yolov5s.pt
```

Once the training is finished, you can visualize the results on your validation set with:
```
python detect.py --weights runs/train/exp/weights/best.pt --source "yolo_dataset/val/*.jpg"
feh runs/detect/exp # or xdg-open/ runs/detect/exp if you don't have feh installed.
```

The detected bounding boxes are written into image files at runs/detect/exp.

## Concluding

That is all it takes to train an object detector on a custom dataset. Next, you might want to export that model into TensorRT or some other runtime for running inside your robot or app. Check out [this guide](https://github.com/ultralytics/yolov5/issues/251) for tips on how to do that.




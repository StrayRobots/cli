# Running detectron2 training in a Docker container

`Dockerfile` defines a docker image with the latest Detectron2 repo (deps/example scripts) available.

Run `docker build -t detectron2-image -f docker/detectron2/Dockerfile .` inside the CLI directory to build the image. You can start an interactive container with `docker run -v <dataset> --gpus all -it  detectron2-image`. 

Inside a container, a simple example can be run with:

```
wget http://images.cocodataset.org/val2017/000000439715.jpg -O input.jpg
python3 demo/demo.py  \
	--config-file configs/COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml \
	--input input.jpg --output outputs/ \
	--opts MODEL.WEIGHTS detectron2://COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x/137849600/model_final_f10217.pkl
```

TODO:
1) Lock a detectron2 version (specific commit/version)
2) Allow running different training scripts inside container
3) Read "training configs" from a stray model directory

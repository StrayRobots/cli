# Running detectron2 training in a Docker container

## Build image
From the root of the repository, run `docker build -t detectron2. -f docker/detectron2/Dockerfile`

## Push image to registry (requires login)

`docker tag detectron2 strayrobots/detectron2:latest && docker push strayrobots/detectron2:latest`

## Run container

```
docker run -v <dataset>:/home/appuser/data -v <model>:/home/appuser/detectron2-model --gpus all -it  strayrobots/detectron2:latest \
            --dataset /home/appuser/data \
            --model /home/appuser/detectron2-model \
            --num-gpus <num_gpus>
```

# Running detectron2 training in a Docker container

## Build image
From the root of the repository, run `docker build -t detectron2 . -f docker/detectron2/Dockerfile`

## Push image to registry (requires login)

`docker tag detectron2 strayrobots/detectron2:latest && docker push strayrobots/detectron2:latest`


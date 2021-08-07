# Running calibration in a Docker container

## Build image
`docker build -t calibrate .` in this directory ()

## Push image to registry (requires login)

`docker tag calibrate strayrobots/calibrate:latest && docker push strayrobots/calibrate:latest`

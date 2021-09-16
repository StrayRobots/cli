# Running calibration in a Docker container

## Build image
`docker build -t calibrate . -f docker/calibrate/Dockerfile` at the root of the repository.

## Push image to registry (requires login)

Run at the root of the repository:
```
docker build -t calibrate . -f docker/calibrate/Dockerfile
docker tag calibrate strayrobots/calibrate:latest && docker push strayrobots/calibrate:latest`
```


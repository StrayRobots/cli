
# Docker configuration for running ORBSlam + Open3D based integration

## Build image

From the root of the repository, run `docker build -t integrate . -f docker/orbslam/Dockerfile`.

## Push image to registry (requires login)

Again, from the root, run:
```
docker build -t integrate . -f docker/orbslam/Dockerfile
docker tag integrate strayrobots/integrate:latest && docker push strayrobots/integrate:latest
```


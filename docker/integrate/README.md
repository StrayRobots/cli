
# Docker configuration for running ORBSlam + Open3D based integration

## Build image

From the root of the repository, run `docker build -t integrate . -f docker/integrate/Dockerfile`.

## Push image to registry (requires login)

Again, from the root, run:
```
docker build -t integrate . -f docker/integrate/Dockerfile
docker tag integrate strayrobots/integrate:latest && docker push strayrobots/integrate:latest
```

## The entrypoint validates a keygen.sh license key
1. Add `export STRAY_LICENSE_KEY=<key>`into bashrc etc.
2. Run docker the container with `docker run -e STRAY_LICENSE_KEY=${STRAY_LICENSE_KEY} ...`


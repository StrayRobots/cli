
# Docker configuration for running ORBSlam + Open3D based integration

## Build image
`docker build -t integrate .` in this directory ()

## Push image to registry (requires login)

`docker tag integrate strayrobots/integrate:latest && docker push strayrobots/integrate:latest`

## Run container

Run with `./run.sh <path-to-scene>` to integrate the scene that was passed in.


#!/bin/bash

set -e

aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 458238174020.dkr.ecr.eu-west-1.amazonaws.com
docker build -t scene-integration .
docker tag scene-integration:latest 458238174020.dkr.ecr.eu-west-1.amazonaws.com/scene-integration:latest
docker push 458238174020.dkr.ecr.eu-west-1.amazonaws.com/scene-integration:latest


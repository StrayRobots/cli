#!/bin/bash

branch="$1"
shift
scenes=$@

# Hack to encode the parameters as json array.
scene_string=$(python3 -c 'import sys; print(", ".join([f"\"{a}\"" for a in sys.argv[1:]]))' $@)
container_command="[\"$branch\", $scene_string]"

echo "Scheduling container with commands $container_command"
echo "{\"containerOverrides\": [{ \"name\": \"scene-integrator\", \"command\": $container_command }]}"

aws ecs run-task --cluster arn:aws:ecs:eu-west-1:458238174020:cluster/scene-integration-cluster \
	--task-definition integration-task:2 \
	--network-configuration 'awsvpcConfiguration={subnets=[subnet-0050a79c5abc9ba5b],securityGroups=[sg-003db9ff8255ca291],assignPublicIp=ENABLED}' \
    	--overrides "{\"containerOverrides\": [{ \"name\": \"scene-integrator\", \"command\": $container_command }]}"


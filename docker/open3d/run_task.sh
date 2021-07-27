#!/bin/bash

branch="$1"
shift
scenes=$@

# Schedule runs one scene at the time. They can then run in parallel at the same cost,
# the duplicate work is smaller if they are killed for being spot tasks and
# you don't run the risk of the container running out of disk space.
for scene in $scenes; do
	container_command="[\"$branch\", \"$scene\"]"
	echo "Scheduling container with commands $container_command"
	echo "{\"containerOverrides\": [{ \"name\": \"scene-integrator\", \"command\": $container_command }]}"
	aws ecs run-task --cluster arn:aws:ecs:eu-west-1:458238174020:cluster/scene-integration-cluster \
		--task-definition integration-task:3 \
		--network-configuration 'awsvpcConfiguration={subnets=[subnet-0050a79c5abc9ba5b],securityGroups=[sg-003db9ff8255ca291],assignPublicIp=ENABLED}' \
		--overrides "{\"containerOverrides\": [{ \"name\": \"scene-integrator\", \"command\": $container_command }]}"
done




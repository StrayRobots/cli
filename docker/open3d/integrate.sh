#!/bin/bash

set -e

branch="main"
if [[ $1 ]]; then
	branch="$1"
	shift
fi
scenes=$@

echo "Branch $branch scenes $scenes"

echo "Cloning data repository"

echo "$SSH_PRIVATE_KEY" > /root/.ssh/id_integration
chmod 600 /root/.ssh/id_integration
touch /root/.ssh/known_hosts
ssh-keyscan github.com >> /root/.ssh/known_hosts

git clone git@github.com:StrayRobots/StrayData.git /root/data/

pushd /root/data

git checkout $branch

dvc remote add --global spaces s3://stray-data/StrayData
dvc remote modify --global spaces endpointurl https://nyc3.digitaloceanspaces.com
dvc remote modify --global spaces access_key_id "$SPACES_ACCESS_KEY"
dvc remote modify --global spaces secret_access_key "$SPACES_SECRET_ACCESS_KEY"

for scene_subpath in $scenes; do
	scene="/root/data/$scene_subpath"

	if [ ! -d $scene ]; then
		echo "$scene not a directory"
		continue
	fi

	# Retry on error for dvc pull.
	set +e
	for attempt in $(seq 5); do
		dvc pull -R "$scene"
		exit_code=$?
		if [ $exit_code == 1 ]; then
			# The download may fail for being throttled by the remote. Could be some other
			# reason, but seems dvc always exits with code 1 if it fails.
			# Let's retry a few times any way
			echo "dvc pull retrying after attempt $attempt."
			random_wait=$(seq 10 | sort -R | tail -n 1)
			sleep $((50 + $random_wait))
		else
			echo "dvc exit code: $exit_code. Moving on."
			break
		fi
	done
	set -e

	if [[ -f "$scene/scene/integrated.ply.dvc" ]]; then
		echo "$(basename $scene) has already been integrated. Skipping integration."
		continue
	fi

	echo "Integrating scene $scene"

	pushd /root/open3d/reconstruction_system
	python3.8 /root/workspace/create_config.py $scene /root/workspace/config.json
	echo "Making fragments."
	python3.8 run_system.py /root/workspace/config.json --make
	echo "Registering fragments."
	python3.8 run_system.py /root/workspace/config.json --register
	echo "Refining rough registrations."
	python3.8 run_system.py /root/workspace/config.json --refine
	echo "Integrating scene."
	python3.8 run_system.py /root/workspace/config.json --integrate
	echo "Running simultaneous localization and calibration."
	python3.8 run_system.py /root/workspace/config.json --slac --slac_integrate
	popd

	dvc add $scene/slac/0.050/optimized_trajectory_slac.log
	dvc add $scene/slac/0.050/output_slac_mesh.ply
	dvc add $scene/scene/integrated.ply
	dvc add $scene/scene/trajectory.log
	dvc push

	git add $scene/slac/0.050/optimized_trajectory_slac.log.dvc
	git add $scene/slac/0.050/output_slac_mesh.ply.dvc
	git add $scene/slac/0.050/.gitignore
	git add $scene/scene/integrated.ply.dvc
	git add $scene/scene/trajectory.log.dvc
	git add $scene/scene/.gitignore
	git pull --ff origin $branch
	git commit -m "Integrate scene $(basename $scene)"
	git push origin $branch
done

popd


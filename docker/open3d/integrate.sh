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
cat /root/.ssh/id_integration
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

	dvc pull -R "$scene"

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
	# echo "Running simultaneous localization and calibration."
	# python3.8 run_system.py /root/workspace/config.json --slac --slac_integrate
	popd

	dvc add $scene/scene/integrated.ply
	dvc add $scene/scene/trajectory.log
	dvc push

	git add $scene/scene/integrated.ply.dvc
	git add $scene/scene/trajectory.log.dvc
	git add $scene/scene/.gitignore
	git commit -m "Integrate scene $(basename $scene)"

	git push origin testing
done

popd


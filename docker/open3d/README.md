
# Running integration in the cloud

`Dockerfile` defines a docker image which pulls a scene from the data repository and runs Open3D integration.

Use `./update_container.sh` to build the container and upload it to the AWS container registry.

A task can be scheduled to run integration in the AWS Elastic Container Service with the script `./run_task.sh <git-branch> <scene1-path> <scene2-path> ...`. `<git-branch>` should be the branch of the data repository to checkout. At least one scene needs to be specified, but you can list several. The scene paths are relative to the root of the [data repository](https://github.com/StrayRobots/StrayData).


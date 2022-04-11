![Stray Toolkit](/images/stray-logo.png)

# Stray Toolkit Documentation

Welcome to the Stray toolkit documentation! The Stray toolkit allows you to skip building computer vision models from scratch. Deploy custom detection models in days, not weeks.

## Installation

The Stray Command Line Tool and Stray Studio can be installed using our install script. We currently support macOS and Linux based systems.

The script installs the tool and Studio into your home directory into a folder called `.stray`. Some commands are implemented as Docker containers (e.g. `integrate`), which means you need to have Docker installed and the daemon running.

To install Docker, follow the instructions [here](https://docs.docker.com/get-docker/).

For example, the `integrate` command uses CUDA 11 through Nvidia Docker. This requires an Nvidia GPU with a driver capable of running CUDA 11. To install the nvidia-docker runtime, follow the instructions [here](https://github.com/NVIDIA/nvidia-docker).

The Stray toolkit can be installed by running this command in your shell:
```
curl --proto '=https' --tlsv1.2 -sSf https://stray-builds.ams3.digitaloceanspaces.com/cli/install.sh | bash
```

Then source your environment with `source ~/.bashrc` or `source ~/.zshrc` if you are using zsh.

## Uninstall

If you want to uninstall the toolkit, simply delete the `.stray` directory with `rm -rf ~/.stray`.

## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and support.


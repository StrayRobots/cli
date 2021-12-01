# Install

The Stray Command Line Tool and Stray Studio can be installed using our install script. We currently support macOS and Linux based systems.

The script installs the tool and Studio into your home directory into a folder called `.stray`. Some commands are implemented as Docker containers (e.g. `calibration`, `model` and `studio integrate`), which means you will have to have Docker installed and the daemon running.

To install Docker, follow the instructions [here](https://docs.docker.com/get-docker/).

If you want to use the `photogrammetry` command, this requires CUDA through Nvidia Docker. To install this, follow the instructions [here](https://github.com/NVIDIA/nvidia-docker).

Other commands are implemented as Python scripts and compiled programs. These are installed into the `.stray` directory.

To install the toolkit run this command in your shell:
```
curl --proto '=https' --tlsv1.2 -sSf https://stray-builds.ams3.digitaloceanspaces.com/cli/install.sh | bash
```

Then source your environment with `source ~/.bashrc` or `source ~/.zshrc` if you are using zsh.

By installing and using the toolkit and our services, you are agreeing to our [terms of service](/terms/terms-of-service.md).

## Uninstall

If you want to uninstall the toolkit, simply delete the `.stray` directory with `rm -rf ~/.stray`.

## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.

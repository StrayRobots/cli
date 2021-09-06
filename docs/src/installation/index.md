# Install

The Stray Command Line Tool and Stray Studio can be installed using our install script. We currently support macOS and Linux based systems.

The script installs the tool and Studio into your home directory into a folder called `.stray`. Some commands are implemented as Docker containers (e.g. `calibration`, `model` and `studio integrate`), which means you will have to have Docker installed and the daemon running.

To install Docker, follow the instructions [here](https://docs.docker.com/get-docker/).

Other commands are implemented as Python scripts. These will are installed into a Python environment that is downloaded by the installer into the `.stray` directory.

To install the toolkit run this command in your shell:
```
curl --proto '=https' --tlsv1.2 -sSf https://stray-builds.ams3.digitaloceanspaces.com/cli/install.sh | sh
```

Then source your environment with `source ~/.bashrc` or `source ~/.zshrc` if you are using zsh.

## Uninstall

If you want to uninstall the toolkit, simply delete the `.stray` directory with `rm -rf ~/.stray`.

## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.

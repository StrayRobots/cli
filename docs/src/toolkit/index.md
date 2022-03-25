![Stray Toolkit](/images/stray-logo.png)

# Stray Toolkit Documentation

Welcome to the Stray toolkit documentation! The Stray toolkit allows you to skip building computer vision models from scratch. Deploy custom detection models in days, not weeks.

# Installation

The Stray Command Line Tool and Stray Studio can be installed using our install script. We currently support macOS and Linux based systems.

The script installs the tool and Studio into your home directory into a folder called `.stray`. Some commands are implemented as Docker containers (e.g. `calibration`, `integrate`), which means you will have to have Docker installed and the daemon running.

To install Docker, follow the instructions [here](https://docs.docker.com/get-docker/).

Other commands are implemented as Python scripts and compiled programs. To use these, you should install the `stray` [package](https://github.com/StrayRobots/stray) into your python3 environment (conda/venv).

To install the toolkit run this command in your shell:

```
curl --proto '=https' --tlsv1.2 -sSf https://stray-builds.ams3.digitaloceanspaces.com/cli/install.sh | bash
```

Then source your environment with `source ~/.bashrc` or `source ~/.zshrc` if you are using zsh.

By installing and using the toolkit and our services, you are agreeing to our [terms of service](/terms/terms-of-service.md).

## Uninstall

If you want to uninstall the toolkit, simply delete the `.stray` directory with `rm -rf ~/.stray`.

## Help

Visit our [issue tracker](https://github.com/StrayRobots/stray/issues) for help and direct support.

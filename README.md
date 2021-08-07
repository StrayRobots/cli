# CLI
CLI for using the Stray tools

## Deploying

To deploy package the package, first install `s3cmd` with `brew install s3cmd` or `sudo apt-get install s3cmd`. Then follow the instructions [here](https://docs.digitalocean.com/products/spaces/resources/s3cmd/) to configure it to with your access key to access the stray-build bucket.

You will need to also install `constructor` from [https://github.com/conda/constructor](https://github.com/conda/constructor) to create a deployment.

Run `./ops/deploy.sh` to upload the cli script to Digital Ocean Spaces.

## Installing

To install the latest build from the cloud, simply run `./bin/install.sh`. This will download the latest [Studio](StrayRobots/Studio) and the CLI script from Spaces and install it in `$HOME/.stray/`. It will also update `.bashrc` and `.zshrc` to make the commands available in those shells.


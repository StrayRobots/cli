## Model Format

Stray operates on a standard model format. The model directory can be produced and modified with different Stray [commands](/commands/index.md). A model directory may consists of the following items:

- `model.pth`
    - The current version of the model saved as [TorchScript](https://pytorch.org/docs/stable/jit.html)
    - Models can be created and trained with the `stray model` [command](/commands/model.md)
- `config.json`
    - Contains the optional model type specific configuration for training and inference
    - The editable config files are initialized when running the `stray model generate` [command](/commands/model.md#stray-model-generate)


## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.
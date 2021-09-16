## Model Format

Stray operates on a standard model format. The model directory can be produced and modified with different Stray [commands](/commands/index.md). A model directory consists of the following items:

- `output`
    - Weights and other data are saved here during training. Models can be created and trained with the `stray model` [command](/commands/model.md)
- `config.yaml`
    - Contains the model type specific configuration for training and inference
    - Initialized when running the `stray model generate` [command](/commands/model.md#stray-model-generate)
- `dataset_metadata.json`
    - Metadata (e.g. class labels) from training data is stored here


## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.
# Model

The `model` subcommand is used to generate and train [models](/formats/model.md) that can be evaluated and used for different tasks.

## Available commands
## `stray model generate`

- Generates a new [model directory](/formats/model.md)

#### Options

|name|default|choices|description|
|---|---|---|---|
|`--model-type`|`detectron2`|`detectron2`|The model type to use. Currently only `detectron2` is supported|
|`--repository`| | |Where to save the newly created models|
|`--help, -h`| | |Show help|


## `stray model bake`

- ["Bakes"](https://news.ycombinator.com/item?id=12559435) a dataset into a given [model](/formats/model.md). Saves the model as `model.pth` into the model directory. The model training happens inside a Docker container.

#### Options

|name|default|choices|description|
|-|-|-|-|
|`--dataset`|| |Path to the scene(s) to be baked|
|`--model`| | |Path to the model to be used in baking|
|`--num-gpus`|0| |Number of GPUs to use in baking|
|`--resume`|False| |Resume training from previous run|
|`--help, -h`| | |Show help|

## `stray model evaluate`

- Evaluates model performance against the given evaluation dataset

#### Options

|name|default|choices|description|
|-|-|-|-|
|`--dataset`| | |Path to the scene(s) to be evaluated against|
|`--model`| | |Path to the model to evaluate|
|`--weights`|`model_final.pth`| |Weights file to use for evaluation in the `model/output` directory|
|`--show`| | |Optionally show visual examples of the predictions|
|`--help, -h`| | |Show help|


## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.
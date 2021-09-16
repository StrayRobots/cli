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
|`<scenes>`| | |Paths to the scenes which are used in model training|
|`--model`| | |Path to the model to be used in baking|
|`--num-gpus`|0| |Number of GPUs to use in baking|
|`--resume`|False| (flag) |Resume training from previous run|
|`--segmentation`| False |(flag)|Train a segmentation model, requires segmentation masks to exist (masks can be created with `stray dataset bake`|
|`--bbox-from-mask`| False |(flag)|Determine the 2D bounding boxes from segmentation masks, requires segmentation masks to exist (masks can be created with `stray dataset bake`|
|`--help, -h`| | |Show help|

## `stray model evaluate`

- Evaluates model performance against the given evaluation dataset

#### Options

|name|default|choices|description|
|-|-|-|-|
|`<scenes>`| | |Paths to the scenes to use for evaluation|
|`--model`| | |Path to the model to evaluate|
|`--weights`|`model/output/model_final.pth`| |Path to the weights file to use for evaluation|
|`--threshold`|0.7| |Prediction confidence threshold|
|`--help, -h`| | |Show help|


## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.
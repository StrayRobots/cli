# Label

The `label` subcommand is used to create labels from annotated scenes from Stray [datasets](/formats/data.md) that can be visualized and used by models and tasks.

## Available commands
## `stray label generate`
- Generates labels of different types from annotated [scenes](/formats/data.md)

#### Options

|name|default|choices|description|
|---|---|---|---|
|`--dataset`| | |Path to the [scene(s)](/formats/data.md#dataset-format) that contain annotations created in [Studio](/commands/studio.md#stray-studio-open)|
|`--primitive`| |[Options](/formats/data.md#available-primitives)|Types of labels to generate|
|`--format`| `detectron2` |`detectron2`|Label format to generate (currently only `detectron2` is supported)|
|`--help, -h`| | |Show help|



## `stray label show`

- Displays labels of different types from annotated [scenes](/formats/data.md)

#### Options

|name|default|choices|description|
|---|---|---|---|
|`--dataset`| | |Path to the [scene(s)](/formats/data.md#dataset-format) that contain annotations created in [Studio](/commands/studio.md#stray-studio-open)|
|`--primitive`| |[Options](/formats/data.md#available-primitives)|Types of labels to show|
|`--rate, -r`| 30 | int |Frame rate|
|`--help, -h`| | |Show help|


## Help

Visit our [issue tracker](https://github.com/StrayRobots/issues) for help and direct support.
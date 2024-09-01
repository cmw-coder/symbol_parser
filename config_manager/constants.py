from .types import ActionType, BaseConfig

EXAMPLE_COLLECT_FREE_FUNCTIONS_CONFIG: BaseConfig = {
    "action": ActionType.CollectSymbols,
    "input_folder": "path/to/folder",
    "tags_folder": "path/to/folder",
    "output_folder": "path/to/folder",
}

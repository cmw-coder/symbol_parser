from .types import ActionType, CollectFreeFunctionsConfig

EXAMPLE_COLLECT_FREE_FUNCTIONS_CONFIG: CollectFreeFunctionsConfig = {
    "action": ActionType.CollectFreeFunctions,
    "input_folder": "path/to/folder",
    "tags_folder": "path/to/folder",
    "search_list": [
        {"name": "free_function_1", "free_param_index": 0},
        {"name": "free_function_2", "free_param_index": 1},
    ],
}

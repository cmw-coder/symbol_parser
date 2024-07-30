from enum import StrEnum
from typing import AnyStr, List, TypedDict


class ActionType(StrEnum):
    CollectAllSymbols = "CollectAllSymbols"
    CollectFreeFunctions = "CollectFreeFunctions"


class BaseConfig(TypedDict):
    action: ActionType
    input_folder: AnyStr
    tags_folder: AnyStr
    output_folder: AnyStr


class CollectAllSymbolsConfig(BaseConfig):
    reverse: bool


class BasicFreeFunction(TypedDict):
    name: AnyStr
    free_param_index: int


class CollectFreeFunctionsConfig(BaseConfig):
    search_list: List[BasicFreeFunction]

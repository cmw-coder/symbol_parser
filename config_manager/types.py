from enum import StrEnum
from typing import AnyStr, List, TypedDict


class ActionType(StrEnum):
    CollectSymbols = "CollectSymbols"
    CollectFunctions = "CollectFunctions"


class BaseConfig(TypedDict):
    action: ActionType
    input_folder: AnyStr
    tags_folder: AnyStr
    output_folder: AnyStr


class CollectSymbolsConfig(BaseConfig):
    reverse: bool


class FunctionSearchData(TypedDict):
    name: AnyStr
    param_index: int


class CollectFreeFunctionsConfig(BaseConfig):
    search_list: List[FunctionSearchData]

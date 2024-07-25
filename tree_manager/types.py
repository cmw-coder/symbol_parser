from typing import AnyStr, List, TypedDict


class FreeExpression(TypedDict):
    name: AnyStr
    freed_parameter: AnyStr
    content: AnyStr


class FreedParam(TypedDict):
    name: AnyStr
    index: int


class FreeFunction(TypedDict):
    name: AnyStr
    path: AnyStr
    content: AnyStr
    depth: int
    called_free_expressions: List[FreeExpression]
    freed_params: List[FreedParam]

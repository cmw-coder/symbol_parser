from typing import AnyStr, List, TypedDict


class FreeExpression(TypedDict):
    name: AnyStr
    freed_parameter: AnyStr
    content: AnyStr


class FreedParam(TypedDict):
    name: AnyStr
    index: int


class FreeFunction(TypedDict):
    function_name: AnyStr
    function_path: AnyStr
    function_content: AnyStr
    function_declarator: AnyStr
    depth: int
    called_free_expressions: List[FreeExpression]
    freed_params: List[FreedParam]

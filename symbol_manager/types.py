from enum import Enum
from typing import AnyStr, Dict, TypedDict


class SymbolKind(Enum):
    Enum = "g"
    Enumerators = "e"
    Function = "f"
    Macro = "d"
    Reference = "t"
    Struct = "s"
    Union = "u"
    Variable = "v"


class SymbolRaw(TypedDict):
    name: AnyStr
    path: AnyStr
    kind: SymbolKind
    line: int
    extra_fields: Dict[AnyStr, AnyStr]


class Symbol(TypedDict):
    name: AnyStr
    path: AnyStr
    type: AnyStr
    depth: int
    content: AnyStr
    begin_line: int
    end_line: int

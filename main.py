from glob import glob
from typing import AnyStr, Dict, TypedDict, List

from config_manager import CollectFreeFunctionsConfig, ConfigManager
from os import path
from symbol_manager import Symbol, SymbolManager
from tree_sitter import Language, Node, Parser

import json
import re
import tree_sitter_c


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


def find_typed_nodes(nodes: List[Node], node_type: AnyStr) -> List[Node]:
    result = []
    for node in nodes:
        if node.type == node_type:
            result.append(node)
        if len(node.children) > 0:
            result.extend(
                [
                    item
                    for item in find_typed_nodes(node.children, node_type)
                    if item is not None
                ]
            )

    return result


if __name__ == "__main__":
    language = Language(tree_sitter_c.language())
    parser = Parser(language)
    call_expression_query = language.query(
        "(call_expression"
        "  function: (identifier) @name"
        "  arguments: (argument_list) @arguments"
        ") @expression"
    )
    function_declarator_query = language.query(
        "(function_declarator parameters: (parameter_list) @parameters)"
    )

    config: CollectFreeFunctionsConfig = ConfigManager().config

    symbol_manager = SymbolManager(
        function_tags_path=f"{config['tags_folder']}/function.ctags",
        structure_tags_path=f"{config['tags_folder']}/structure.ctags",
    )

    all_files = glob(f"{config['input_folder']}/**/*.c", recursive=True)
    all_files.extend(glob(f"{config['input_folder']}/**/*.h", recursive=True))

    print(f"Found {len(all_files)} source files")

    free_functions: Dict[AnyStr, Symbol] = {}

    for filename in all_files:
        print(f"Processing '{filename}'")
        symbols = list(symbol_manager.collect_symbols_in_file(filename).values())

        free_functions: List[FreeFunction] = []
        for input_item in [
            symbol
            for symbol in symbols
            if symbol["type"] == "Function" or symbol["type"] == "Macro"
        ]:
            content_bytes = bytes(
                re.sub(r"\b(IN|OUT|INOUT)\b", "", input_item["content"]), "utf-8"
            )
            tree = parser.parse(content_bytes)
            function_declarator_matches = function_declarator_query.matches(
                tree.root_node
            )
            if len(function_declarator_matches) != 1:
                continue

            call_expression_matches = call_expression_query.matches(tree.root_node)
            if len(call_expression_matches) > 0:
                called_free_expressions: List[FreeExpression] = []
                freed_params: List[FreedParam] = []
                for match in [_match[1] for _match in call_expression_matches]:
                    expression = content_bytes[
                        match["expression"].start_byte : match["expression"].end_byte
                    ].decode()
                    name = content_bytes[
                        match["name"].start_byte : match["name"].end_byte
                    ].decode()
                    call_parameters = [
                        content_bytes[item.start_byte : item.end_byte].decode()
                        for item in find_typed_nodes(
                            match["arguments"].children, "identifier"
                        )
                    ]
                    if len(call_parameters) > 0:
                        for search_item in config["search_list"]:
                            if name == search_item["name"]:
                                freed_parameter = call_parameters[
                                    search_item["free_param_index"]
                                ]
                                function_parameters = [
                                    content_bytes[
                                        item.start_byte : item.end_byte
                                    ].decode()
                                    for item in find_typed_nodes(
                                        function_declarator_matches[0][1][
                                            "parameters"
                                        ].children,
                                        "identifier",
                                    )
                                ]
                                if freed_parameter in function_parameters:
                                    freed_params.append(
                                        FreedParam(
                                            name=freed_parameter,
                                            index=function_parameters.index(
                                                freed_parameter
                                            ),
                                        )
                                    )
                                called_free_expressions.append(
                                    FreeExpression(
                                        name=name,
                                        freed_parameter=freed_parameter,
                                        content=expression,
                                    )
                                )
                if len(called_free_expressions) > 0:
                    free_functions.append(
                        FreeFunction(
                            name=input_item["name"],
                            path=input_item["path"],
                            content=input_item["content"],
                            depth=0,
                            called_free_expressions=called_free_expressions,
                            freed_params=freed_params,
                        )
                    )

        json.dump(
            free_functions,
            open(f"{config["output_folder"]}/{path.basename(filename)}_free_functions.json", "w"),
            indent=2,
        )

from tree_sitter import Language, Parser
from typing import List

from .types import FreedParam, FreeExpression, FreeFunction
from .utils import find_nodes_with_type
from config_manager import BasicFreeFunction
from symbol_manager import Symbol

import re


class TreeManager:
    def __init__(self, language_ptr: int):
        language = Language(language_ptr)
        self.__call_expression_query = language.query(
            "(call_expression"
            "  function: (identifier) @name"
            "  arguments: (argument_list) @arguments"
            ") @expression"
        )
        self.__function_declarator_query = language.query(
            "(function_declarator parameters: (parameter_list) @parameters)"
        )
        self.__parser = Parser(language)

    def collect_free_functions(
        self, symbols: List[Symbol], basic_free_functions: List[BasicFreeFunction]
    ) -> List[FreeFunction]:
        free_functions: List[FreeFunction] = []
        for input_item in [
            symbol
            for symbol in symbols
            if symbol["type"] == "Function" or symbol["type"] == "Macro"
        ]:
            content_bytes = bytes(
                re.sub(r"\b(IN|OUT|INOUT)\b", "", input_item["content"]), "utf-8"
            )
            tree = self.__parser.parse(content_bytes)
            function_declarator_matches = self.__function_declarator_query.matches(
                tree.root_node
            )
            if len(function_declarator_matches) != 1:
                continue

            call_expression_matches = self.__call_expression_query.matches(
                tree.root_node
            )
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
                        for item in find_nodes_with_type(
                            match["arguments"].children, "identifier"
                        )
                    ]
                    if len(call_parameters) > 0:
                        for search_item in basic_free_functions:
                            if name == search_item["name"]:
                                freed_parameter = call_parameters[
                                    search_item["free_param_index"]
                                ]
                                function_parameters = [
                                    content_bytes[
                                        item.start_byte : item.end_byte
                                    ].decode()
                                    for item in find_nodes_with_type(
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
        return free_functions

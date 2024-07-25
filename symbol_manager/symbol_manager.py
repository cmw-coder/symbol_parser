from typing import AnyStr, Dict, Optional

from .constants import IGNORE_WORDS, REFERENCE_SYMBOLS
from .types import Symbol
from .utils import construct_symbol, retrieve_symbol_raw, get_most_similar_symbol

import json
import re


class SymbolManager:
    def __init__(self, function_tags_path: AnyStr, structure_tags_path: AnyStr) -> None:
        self.__function_tags_path = function_tags_path
        self.__structure_tags_path = structure_tags_path

    def collect_symbols_in_file(
        self,
        input_file_path: AnyStr,
        output_file_path: Optional[AnyStr] = None,
    ) -> Dict[AnyStr, Symbol]:
        results: Dict[AnyStr, Symbol] = {}

        with open(input_file_path, "r") as main_file:
            depth = 0
            main_symbols = self.collect_symbols_in_content(
                main_file.read(), input_file_path, depth
            )
            if not main_symbols:
                print("No symbols found in main file")
                return results
            results = results | main_symbols
            current_symbols: Dict[AnyStr, Symbol] = {
                key: value
                for key, value in main_symbols.items()
                if value["type"] != "Function" and value["type"] != "Macro"
            }
            while len(current_symbols) > 0:
                depth += 1
                old_length = len(results)
                for _, current_symbol in current_symbols.items():
                    current_symbols = self.collect_symbols_in_content(
                        current_symbol["content"], current_symbol["path"], depth
                    )
                    if len(current_symbols) > 0:
                        results = results | current_symbols
                if old_length == len(results):
                    break

        if output_file_path is not None:
            json.dump(list(results.values()), open(output_file_path, "w"), indent=2)

        return results

    def collect_symbols_in_content(
        self, content: AnyStr, path: AnyStr, depth: int
    ) -> Dict[AnyStr, Symbol]:
        match = re.findall(r"\b[A-Z_a-z][0-9A-Z_a-z]+\b", content)
        filtered = [word for word in match if word not in IGNORE_WORDS]
        results: Dict[AnyStr, Symbol] = {}
        for symbol_str in filtered:
            if symbol_str[:2] == "g_":
                temp_symbol = self.__retrieve_global(symbol_str, path, depth)
            elif symbol_str[-2:] in REFERENCE_SYMBOLS:
                temp_symbol = self.__retrieve_reference(symbol_str, path, depth)
            else:
                temp_symbol = self.__retrieve_function(symbol_str, path, depth)
            if temp_symbol is not None and temp_symbol["name"] not in results:
                results[temp_symbol["name"]] = temp_symbol
        return results

    def __retrieve_function(
        self, symbol_str: AnyStr, path: AnyStr, depth: int
    ) -> Symbol | None:
        raw_list = retrieve_symbol_raw(self.__function_tags_path, symbol_str)
        if len(raw_list) > 0:
            return construct_symbol(get_most_similar_symbol(raw_list, path), depth)

    def __retrieve_global(
        self, symbol_str: AnyStr, path: AnyStr, depth: int
    ) -> Symbol | None:
        raw_list = retrieve_symbol_raw(self.__structure_tags_path, symbol_str)
        if len(raw_list) > 0:
            return construct_symbol(get_most_similar_symbol(raw_list, path), depth)

    def __retrieve_reference(
        self, symbol_str: AnyStr, path: AnyStr, depth: int
    ) -> Symbol | None:
        reference_list = retrieve_symbol_raw(self.__structure_tags_path, symbol_str)
        if len(reference_list) > 0:
            reference = get_most_similar_symbol(reference_list, path)
            if "typeref" in reference["extra_fields"]:
                raw_list = retrieve_symbol_raw(
                    self.__structure_tags_path,
                    reference["extra_fields"]["typeref"].split(":", 1)[1],
                )
                if len(raw_list) > 0:
                    return construct_symbol(
                        get_most_similar_symbol(raw_list, path), depth
                    )
            else:
                return construct_symbol(reference, depth)

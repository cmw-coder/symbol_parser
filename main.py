from glob import glob
from os import path
from typing import AnyStr, Dict, Optional, TypedDict, List

from config_manager import CollectFreeFunctionsConfig, ConfigManager
from symbol_manager import Symbol, SymbolManager

import json
import re


def collect_symbols(
    _symbol_manager: SymbolManager,
    _input_file_path: AnyStr,
    _output_file_path: Optional[AnyStr] = None,
) -> Dict[AnyStr, Symbol]:
    results: Dict[AnyStr, Symbol] = {}

    with open(_input_file_path, "r") as main_file:
        depth = 0
        main_symbols = _symbol_manager.collect_symbols(
            main_file.read(), _input_file_path, depth
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
                current_symbols = _symbol_manager.collect_symbols(
                    current_symbol["content"], current_symbol["path"], depth
                )
                if len(current_symbols) > 0:
                    results = results | current_symbols
            if old_length == len(results):
                break

    if _output_file_path is not None:
        json.dump(list(results.values()), open(_output_file_path, "w"), indent=2)

    return results


class FreeFunction(TypedDict):
    name: AnyStr
    path: AnyStr
    content: AnyStr
    depth: int
    free_param_indexes: List[int]
    free_line_indexes: List[int]


if __name__ == "__main__":
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
        symbols = collect_symbols(symbol_manager, filename)

        free_functions: List[FreeFunction] = []
        for input_item in symbols.values():
            free_line_indexes: List[int] = []
            for index, content_line in enumerate(input_item["content"].splitlines()):
                if any(
                    re.search(f"\\b{search_item['name']}\\b", content_line)
                    for search_item in config["search_list"]
                ):
                    free_line_indexes.append(index)
            if len(free_line_indexes) > 0:
                free_functions.append(
                    {
                        "name": input_item["name"],
                        "path": input_item["path"],
                        "content": input_item["content"],
                        "depth": 0,
                        "free_param_indexes": [0],
                        "free_line_indexes": free_line_indexes,
                    }
                )
        json.dump(
            free_functions,
            open(f"{path.basename(filename)}_free_functions.json", "w"),
            indent=2,
        )

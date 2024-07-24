from argparse import ArgumentParser
from glob import glob
from typing import AnyStr, Dict, Optional

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


if __name__ == "__main__":
    config: CollectFreeFunctionsConfig = ConfigManager().config

    symbol_manager = SymbolManager(
        function_tags_path=f"{config["tags_folder"]}/function.ctags",
        structure_tags_path=f"{config["tags_folder"]}/structure.ctags",
    )

    all_files = glob(f"{config["input_folder"]}/**/*.c", recursive=True)
    all_files.extend(glob(f"{config["input_folder"]}/**/*.h", recursive=True))

    print(f"Found {len(all_files)} source files")

    for filename in all_files:
        print(f"Processing '{filename}'")
        symbols = collect_symbols(symbol_manager, filename)
        result = [
            input_item
            for input_item in symbols.values()
            if any(
                re.search(f"\\b{search_item["name"]}\\b", input_item["content"])
                for search_item in config["search_list"]
            )
        ]
        print(json.dumps(result, indent=2))

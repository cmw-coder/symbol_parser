from os import path
from pathlib import Path
from typing import List

from config_manager import (
    ActionType,
    FunctionSearchData,
    CollectSymbolsConfig,
    CollectFreeFunctionsConfig,
    ConfigManager,
)
from symbol_manager import Symbol
from tree_manager import TreeManager

import json
import tree_sitter_c


if __name__ == "__main__":
    tree_manager = TreeManager(tree_sitter_c.language())
    config_manager = ConfigManager()
    action = config_manager.action
    input_files = config_manager.input_files
    output_folder = config_manager.output_folder
    symbol_manager = config_manager.use_symbol_manager()

    reverse: bool = False
    search_list: List[FunctionSearchData] = []
    if action == ActionType.CollectSymbols:
        specific_config: CollectSymbolsConfig = config_manager.use_specific_config(
            CollectSymbolsConfig
        )
        if "reverse" in specific_config:
            reverse = specific_config["reverse"]
        else:
            raise ValueError("'reverse' not found in config")
    elif action == ActionType.CollectFunctions:
        specific_config: CollectFreeFunctionsConfig = (
            config_manager.use_specific_config(CollectFreeFunctionsConfig)
        )
        if "search_list" in specific_config:
            search_list = specific_config["search_list"]
        else:
            raise ValueError("'search_list' not found in config")
    else:
        raise ValueError(f"Unknown action '{action}'")

    Path(output_folder).mkdir(parents=True, exist_ok=True)

    print(f"Start '{action}' action")
    print(f"Found {len(input_files)} source files")

    for file_index, filename in enumerate(input_files):
        process_indicator = f"[{file_index + 1}/{len(input_files)}]"
        print(f"{process_indicator} Processing '{filename}'...")

        symbols: List[Symbol] = list(
            symbol_manager.collect_symbols_in_file(filename, reverse).values()
        )
        print(f"{process_indicator} Found {len(symbols)} symbols")

        if action == ActionType.CollectSymbols:
            output_path = f"{output_folder}/{path.basename(filename)}_symbols.json"
            json.dump(symbols, open(output_path, "w"), indent=2)
            print(f"{process_indicator} Saved symbols to '{output_path}'")
        elif action == ActionType.CollectFunctions:
            free_functions = tree_manager.collect_free_functions(symbols, search_list)
            print(f"{process_indicator} Found {len(free_functions)} free functions")

            output_path = (
                f"{output_folder}/{path.basename(filename)}_free_functions.json"
            )
            json.dump(
                free_functions,
                open(
                    output_path,
                    "w",
                ),
                indent=2,
            )
            print(f"{process_indicator} Saved free functions to '{output_path}'")

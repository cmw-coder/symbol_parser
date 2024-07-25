from glob import glob
from os import path
from typing import List

from config_manager import CollectFreeFunctionsConfig, ConfigManager
from symbol_manager import Symbol, SymbolManager
from tree_manager import TreeManager

import json
import tree_sitter_c


if __name__ == "__main__":
    tree_manager = TreeManager(tree_sitter_c.language())

    config: CollectFreeFunctionsConfig = ConfigManager().config

    symbol_manager = SymbolManager(
        function_tags_path=f"{config['tags_folder']}/function.ctags",
        structure_tags_path=f"{config['tags_folder']}/structure.ctags",
    )

    all_files = glob(f"{config['input_folder']}/**/*.c", recursive=True)
    all_files.extend(glob(f"{config['input_folder']}/**/*.h", recursive=True))

    print(f"Found {len(all_files)} source files")

    for file_index, filename in enumerate(all_files):
        process_indicator = f"[{file_index}/{len(all_files)}]"
        print(f"{process_indicator} Processing '{filename}'...")

        symbols: List[Symbol] = list(
            symbol_manager.collect_symbols_in_file(filename).values()
        )
        print(f"{process_indicator} Found {len(symbols)} symbols")

        free_functions = tree_manager.collect_free_functions(
            symbols, config["search_list"]
        )
        print(f"{process_indicator} Found {len(free_functions)} free functions")
        json.dump(
            free_functions,
            open(
                f"{config['output_folder']}/{path.basename(filename)}_free_functions.json",
                "w",
            ),
            indent=2,
        )

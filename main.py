from typing import AnyStr, Dict

from symbol_manager import Symbol, SymbolManager

import json


if __name__ == "__main__":
    results: Dict[AnyStr, Symbol] = {}
    symbol_manager = SymbolManager(
        function_tags_path="assets/function.ctags",
        structure_tags_path="assets/structure.ctags",
    )

    main_file_path = "assets/main.c"

    with open(main_file_path, "r") as main_file:
        depth = 0
        main_symbols = symbol_manager.collect_symbols(
            main_file.read(), main_file_path, depth
        )
        if not main_symbols:
            print("No symbols found in main file")
            exit(1)
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
                current_symbols = symbol_manager.collect_symbols(
                    current_symbol["content"], current_symbol["path"], depth
                )
                if len(current_symbols) > 0:
                    results = results | current_symbols
            if old_length == len(results):
                break

    json.dump(list(results.values()), open("results.json", "w"), indent=2)

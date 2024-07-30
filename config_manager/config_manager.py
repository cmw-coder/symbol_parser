from argparse import ArgumentParser
from glob import glob
from typing import cast, TypeVar

from .constants import EXAMPLE_COLLECT_FREE_FUNCTIONS_CONFIG
from .types import BaseConfig

import json

T = TypeVar("T")


class ConfigManager:
    def __init__(self):
        arg_parser = ArgumentParser(
            prog="Symbol Parser",
            description="Parse symbol data from CTags and source files",
        )
        arg_parser.add_argument(
            "config_file",
            type=str,
            help=f"JSON config file, format: {json.dumps(EXAMPLE_COLLECT_FREE_FUNCTIONS_CONFIG, indent=2)}",
        )
        args = arg_parser.parse_args()
        self.__config: BaseConfig = json.load(open(args.config_file, "r"))
        if "action" not in self.__config or not self.__config["action"]:
            raise ValueError("'action' not found in config")
        if "input_folder" not in self.__config or not self.__config["input_folder"]:
            raise ValueError("'input_folder' not found in config")
        if "tags_folder" not in self.__config or not self.__config["tags_folder"]:
            raise ValueError("'tags_folder' not found in config")
        if "output_folder" not in self.__config or not self.__config["output_folder"]:
            raise ValueError("'output_folder' not found in config")

    @property
    def action(self):
        return self.__config["action"]

    @property
    def input_files(self):
        all_files = glob(f"{self.__config['input_folder']}/**/*.c", recursive=True)
        all_files.extend(
            glob(f"{self.__config['input_folder']}/**/*.h", recursive=True)
        )
        return all_files

    @property
    def output_folder(self):
        return self.__config["output_folder"]

    def use_specific_config(self, cast_type: T):
        return cast(cast_type, self.__config)

    def use_symbol_manager(self):
        from symbol_manager import SymbolManager

        return SymbolManager(
            function_tags_path=f"{self.__config['tags_folder']}/function.ctags",
            structure_tags_path=f"{self.__config['tags_folder']}/structure.ctags",
        )

from argparse import ArgumentParser

from .constants import EXAMPLE_COLLECT_FREE_FUNCTIONS_CONFIG

import json


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
        self.config = json.load(open(args.config_file, "r"))

    def get(self, section, key):
        return self.config.get(section, key)

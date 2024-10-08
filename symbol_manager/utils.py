from chardet import universaldetector
from difflib import SequenceMatcher
from typing import AnyStr, List, TextIO

from .types import Symbol, SymbolKind, SymbolRaw

import itertools
import subprocess


def construct_symbol(symbol_raw: SymbolRaw, depth: int) -> Symbol:
    if "end" in symbol_raw["extra_fields"]:
        end_line = int(symbol_raw["extra_fields"]["end"])
    else:
        end_line = symbol_raw["line"] + 1
    try:
        return {
            "name": symbol_raw["name"],
            "path": symbol_raw["path"],
            "type": symbol_raw["kind"].name,
            "content": "".join(
                itertools.islice(
                    open_read_file(symbol_raw["path"]),
                    symbol_raw["line"] - 1,
                    end_line,
                )
            ),
            "depth": depth,
            "begin_line": symbol_raw["line"],
            "end_line": end_line,
        }
    except IOError:
        print("Error reading file: ", symbol_raw["path"])


def open_read_file(file_path) -> TextIO:
    encoding: AnyStr
    with open(file_path, "rb") as file:
        detector = universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    encoding = detector.result["encoding"]
    return open(file_path, "r", encoding=encoding, errors="backslashreplace")


def retrieve_symbol_raw(tags_path: AnyStr, symbol_str: AnyStr) -> List[SymbolRaw]:
    result = subprocess.run(
        [
            "readtags",
            "-e",
            "-n",
            "-t",
            tags_path,
            symbol_str,
        ],
        capture_output=True,
        encoding="gbk",
        errors="backslashreplace",
        text=True,
    )

    symbol_raws: List[SymbolRaw] = []

    if result.returncode == 0:
        for entry in result.stdout.split("\n"):
            elements = entry.split("\t")
            if len(elements) >= 5:
                name, path, _, kind_str = elements[:4]
                if elements[4].startswith("line:"):
                    line_str = elements[4]
                    remained_elements = elements[5:]
                else:
                    line_str = elements[5]
                    remained_elements = elements[6:]
                try:
                    symbol_raws.append(
                        {
                            "name": name,
                            "path": path,
                            "kind": SymbolKind(kind_str[5:]),
                            "line": int(line_str[5:]),
                            "extra_fields": {
                                k.split(":", 1)[0]: k.split(":", 1)[1]
                                for k in remained_elements
                            },
                        }
                    )
                except ValueError:
                    pass
    else:
        print("Error retrieving function tags: ", result.stderr)

    return symbol_raws


def get_most_similar_symbol(paths: List[SymbolRaw], path: AnyStr) -> SymbolRaw:
    return max(
        paths,
        key=lambda x: SequenceMatcher(None, path, x["path"]).ratio(),
    )

from tree_sitter import Node
from typing import AnyStr, List


def find_nodes_with_type(nodes: List[Node], node_type: AnyStr) -> List[Node]:
    result = []
    for node in nodes:
        if node.type == node_type:
            result.append(node)
        if len(node.children) > 0:
            result.extend(
                [
                    item
                    for item in find_nodes_with_type(node.children, node_type)
                    if item is not None
                ]
            )

    return result

from .inline import INLINE_ELEMENTS
from random import random

import math


def is_inline(value: dict | str) -> bool:
    """Validate if block or string could be considered inline."""
    return isinstance(value, str) or value.get("type") in INLINE_ELEMENTS


def wrap_text(value: str, as_list: bool = False) -> dict | list[dict]:
    """Wrap a value into a valid sub object."""
    response = {"text": value}
    return [response] if as_list else response


def is_simple_text(data: dict) -> bool:
    keys = set(data.keys())
    return keys == {"text"}


def _just_children(data: dict) -> bool:
    keys = set(data.keys())
    return keys == {"children"}


def flatten_children(raw_block_children: list[dict | list]) -> list[dict]:
    block_children = []
    for block in raw_block_children:
        if isinstance(block, list):
            block_children.extend(block)
        elif not block:
            continue
        elif _just_children(block):
            block_children.extend(block["children"])
        else:
            block_children.append(block)
    return block_children


def group_text_blocks(block_children: list[dict]) -> list[dict]:
    """Group text objects."""
    blocks = []
    text_block = False
    for block in flatten_children(block_children):
        text = block.get("text", "")
        is_text_block = is_simple_text(block)
        if not text_block and is_text_block:
            text_block = block
        elif is_text_block:
            # Preserve whitespaces
            if len(text):
                text_block["text"] += f"{text}"
        elif text_block and not is_text_block:
            blocks.append(text_block)
            text_block = None
            blocks.append(block)
        else:
            blocks.append(block)
    if text_block:
        blocks.append(text_block)
    return blocks


def has_internal_block(block_children: list[dict]) -> bool:
    status = False
    for child in block_children:
        status = status or is_inline(child)
    return status


def normalize_block_nodes(block_children: list, tag_name: str = "span") -> list:
    nodes = []
    # Avoid nesting similar tags
    for node in group_inline_nodes(block_children, tag_name):
        node_children = node.get("children", [])
        if len(node_children) == 1:
            node = node_children[0]
        nodes.append(node)
    return nodes


def group_inline_nodes(block_children: list, tag_name: str = "span") -> list:
    nodes = []
    inline_nodes = None
    for child in block_children:
        if is_inline(child):
            if inline_nodes is None:
                inline_nodes = {"type": tag_name, "children": [child]}
            else:
                inline_nodes["children"].append(child)
        else:
            if inline_nodes:
                nodes.append(inline_nodes)
            inline_nodes = None
            nodes.append(child)
    if inline_nodes:
        nodes.append(inline_nodes)
    return nodes


def process_children(block: dict) -> dict:
    """Handle cases where children is an empty list."""
    if block.get("children") == []:
        block["children"] = wrap_text("", True)
    return block


def _get_id() -> str:
    """Return a key to be used with a table block."""
    id_ = math.floor(random() * math.exp2(24))  # noQA: S311
    return f"{id_}"


def table(
    rows: list[dict | str],
    css_classes: list[str],
    hide_headers: bool = False,
) -> dict:
    table = {
        "basic": False,
        "celled": True,
        "compact": False,
        "fixed": True,
        "inverted": False,
        "rows": rows,
        "striped": False,
        "hideHeaders": hide_headers,
    }
    if "ui" in css_classes and "table" in css_classes:
        styles = ["basic", "celled", "compact", "fixed", "striped"]
        for k in styles:
            if k in css_classes:
                table[k] = True
    return table


def table_row(cells: list[str]) -> dict:
    return {
        "key": _get_id(),
        "cells": cells,
    }


def table_cell(cell_type: str, value: list[dict | str]) -> dict:
    return {
        "key": _get_id(),
        "type": cell_type,
        "value": value,
    }


def invalid_subblock(block: dict) -> bool:
    """Check if block should not be a child of a slate block."""
    type_ = block.get("@type", "")
    return bool(type_)

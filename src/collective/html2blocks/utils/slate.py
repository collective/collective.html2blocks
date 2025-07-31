from .inline import INLINE_ELEMENTS
from collective.html2blocks import _types as t
from random import random

import math


def is_inline(value: t.SlateBlockItem | str) -> bool:
    """Validate if block or string could be considered inline."""
    return isinstance(value, str) or value.get("type") in INLINE_ELEMENTS


def wrap_text(value: str) -> t.SlateBlockItem:
    """Wrap a value into a valid sub object."""
    response: t.SlateBlockItem = {"text": value}
    return response


def wrap_paragraph(value: list[t.SlateBlockItem]) -> t.SlateBlockItem:
    """Wrap a value in to paragraph sub object."""
    return {
        "type": "p",
        "children": value,
    }


def is_simple_text(data: t.SlateBlockItem) -> bool:
    keys = set(data.keys())
    return keys == {"text"}


def _group_top_level(
    items: list[t.SlateBlockItem],
) -> list[tuple[list[t.SlateBlockItem], bool]]:
    """Group top-level items to be wrapped."""
    flags = [is_inline(item) or is_simple_text(item) for item in items]
    groups = []
    current_group = [items[0]]
    last_flag = flags[0]
    for i in range(1, len(items)):
        last_flag = flags[i - 1]
        if flags[i] != last_flag:
            groups.append((current_group, last_flag))
            current_group = [items[i]]
        else:
            current_group.append(items[i])

    groups.append((current_group, last_flag))
    return groups


def process_top_level_items(
    raw_value: list[t.SlateBlockItem],
) -> list[t.SlateBlockItem]:
    """Process top-level items and ensure they are always wrapped."""
    raw_value = raw_value or []
    value = []
    groupped = _group_top_level(raw_value)
    for group, should_wrap in groupped:
        if should_wrap:
            value.append(wrap_paragraph(group))
        else:
            value.extend(group)
    return value


def remove_empty_text(value: list[t.SlateBlockItem]) -> list[t.SlateBlockItem]:
    new_value = []
    for item in value:
        if is_simple_text(item) and not item.get("text", "").strip():
            continue
        new_value.append(item)
    return new_value


def _just_children(data: t.SlateBlockItem) -> bool:
    keys = set(data.keys())
    return keys == {"children"}


def flatten_children(
    raw_block_children: list[t.SlateBlockItem | list],
) -> list[t.SlateBlockItem]:
    block_children = []
    for block in raw_block_children:
        if isinstance(block, list):
            block_children.extend(block)
        elif not block:
            continue
        elif _just_children(block):
            children = block.get("children", [])
            if children:
                block_children.extend(children)
        else:
            block_children.append(block)
    return block_children


def group_text_blocks(block_children: list[t.SlateBlockItem]) -> list[t.SlateBlockItem]:
    """Group text objects."""
    blocks = []
    text_block: t.SlateBlockItem | None = None
    for block in flatten_children(block_children):
        text = block.get("text", "")
        is_text_block = is_simple_text(block)
        if is_text_block and not text_block:
            text_block = block
        elif is_text_block and text_block:
            # Preserve whitespaces
            if len(text):
                cur_text = text_block.get("text", "")
                if cur_text:
                    text_block["text"] = f"{cur_text}{text}"
        elif text_block and not is_text_block:
            blocks.append(text_block)
            text_block = None
            blocks.append(block)
        else:
            blocks.append(block)
    if text_block:
        blocks.append(text_block)
    return blocks


def has_internal_block(block_children: list[t.SlateBlockItem]) -> bool:
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
    inline_nodes: t.SlateBlockItem | None = None
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


def process_children(block: t.SlateBlockItem) -> t.SlateBlockItem:
    """Handle cases where children is an empty list."""
    if block.get("children") == []:
        block["children"] = [wrap_text("")]
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


def table_row(cells: list[t.SlateBlockItem]) -> t.SlateBlockItem:
    return {
        "key": _get_id(),
        "cells": cells,
    }


def table_cell(cell_type: str, value: t.SlateBlockItem) -> t.SlateBlockItem:
    return {
        "key": _get_id(),
        "type": cell_type,
        "value": value,
    }


def invalid_subblock(block: t.SlateBlockItem | t.VoltoBlock) -> bool:
    """Check if block should not be a child of a slate block."""
    type_ = block.get("@type", "")
    return bool(type_)

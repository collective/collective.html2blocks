"""
Slate block utilities for ``collective.html2blocks``.

This module provides functions for manipulating Slate block items, including
wrapping, flattening, grouping, and normalizing block structures for Volto.

Example:
    .. code-block:: python

        from collective.html2blocks.utils import slate
        block = slate.wrap_text('Hello world')
        paragraph = slate.wrap_paragraph([block])
"""

from .inline import INLINE_ELEMENTS
from collective.html2blocks import _types as t
from random import random

import math


def is_inline(value: t.SlateBlockItem | str) -> bool:
    """
    Check if a block or string is considered inline.

    Args:
        value (SlateBlockItem | str): The value to check.

    Returns:
        bool: ``True`` if inline, ``False`` otherwise.
    """
    return isinstance(value, str) or value.get("type") in INLINE_ELEMENTS


def wrap_text(value: str) -> t.SlateBlockItem:
    """
    Wrap a string value into a SlateBlockItem with text.

    Args:
        value (str): The string to wrap.

    Returns:
        SlateBlockItem: The wrapped text block.

    Example:
        .. code-block:: pycon

            >>> wrap_text('Hello')
            {'text': 'Hello'}
    """
    response: t.SlateBlockItem = {"text": value}
    return response


def wrap_paragraph(value: list[t.SlateBlockItem]) -> t.SlateBlockItem:
    """
    Wrap a list of SlateBlockItems into a paragraph block.

    Args:
        value (list[SlateBlockItem]): The children to wrap.

    Returns:
        SlateBlockItem: The paragraph block.

    Example:
        .. code-block:: pycon

            >>> wrap_paragraph([{'text': 'Hello'}])
            {'type': 'p', 'children': [{'text': 'Hello'}]}
    """
    return {
        "type": "p",
        "children": value,
    }


def is_simple_text(data: t.SlateBlockItem) -> bool:
    """
    Check if a SlateBlockItem is simple text (only has ``text`` key).

    Args:
        data (SlateBlockItem): The block to check.

    Returns:
        bool: ``True`` if simple text, ``False`` otherwise.
    """
    keys = set(data.keys())
    return keys == {"text"}


def _group_top_level(
    items: list[t.SlateBlockItem],
) -> list[tuple[list[t.SlateBlockItem], bool]]:
    """
    Group top-level items for wrapping based on inline status.

    Args:
        items (list[SlateBlockItem]): The items to group.

    Returns:
        list[tuple[list[SlateBlockItem], bool]]: Groups and wrap flags.
    """
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
    """
    Process and wrap top-level items as paragraphs where needed.

    Args:
        raw_value (list[SlateBlockItem]): The items to process.

    Returns:
        list[SlateBlockItem]: The processed items.
    """
    raw_value = raw_value or []
    # Remove empty or null items
    raw_value = [item for item in raw_value if item]
    value = []
    groupped = _group_top_level(raw_value)
    for group, should_wrap in groupped:
        if should_wrap:
            value.append(wrap_paragraph(group))
        else:
            value.extend(group)
    return value


def remove_empty_text(value: list[t.SlateBlockItem]) -> list[t.SlateBlockItem]:
    """
    Remove empty text blocks from a list of SlateBlockItems.

    Args:
        value (list[SlateBlockItem]): The items to filter.

    Returns:
        list[SlateBlockItem]: The filtered items.
    """
    new_value = []
    for item in value:
        if is_simple_text(item) and not item.get("text", "").strip():
            continue
        new_value.append(item)
    return new_value


def _just_children(data: t.SlateBlockItem) -> bool:
    """
    Check if a SlateBlockItem only has ``children``.

    Args:
        data (SlateBlockItem): The block to check.

    Returns:
        bool: ``True`` if only ``children``, ``False`` otherwise.
    """
    keys = set(data.keys())
    return keys == {"children"}


def flatten_children(
    raw_block_children: list[t.SlateBlockItem | list],
) -> list[t.SlateBlockItem]:
    """
    Flatten nested children lists into a single list of SlateBlockItems.

    Args:
        raw_block_children (list[SlateBlockItem | list]): The children to flatten.

    Returns:
        list[SlateBlockItem]: The flattened list.
    """
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
    """
    Group consecutive text blocks, preserving whitespace.

    Args:
        block_children (list[SlateBlockItem]): The blocks to group.

    Returns:
        list[SlateBlockItem]: The grouped blocks.
    """
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
    """
    Check if any child is an inline block.

    Args:
        block_children (list[SlateBlockItem]): The children to check.

    Returns:
        bool: ``True`` if any child is inline, ``False`` otherwise.
    """
    status = False
    for child in block_children:
        status = status or is_inline(child)
    return status


def normalize_block_nodes(block_children: list, tag_name: str = "span") -> list:
    """
    Normalize block nodes, avoiding nested similar tags.

    Args:
        block_children (list): The block nodes to normalize.
        tag_name (str, optional): The tag name to use. Defaults to ``span``.

    Returns:
        list: The normalized nodes.
    """
    nodes = []
    # Avoid nesting similar tags
    for node in group_inline_nodes(block_children, tag_name):
        node_children = node.get("children", [])
        if len(node_children) == 1:
            node = node_children[0]
        nodes.append(node)
    return nodes


def group_inline_nodes(block_children: list, tag_name: str = "span") -> list:
    """
    Group inline nodes together under a common tag.

    Args:
        block_children (list): The nodes to group.
        tag_name (str, optional): The tag name to use. Defaults to ``span``.

    Returns:
        list: The grouped nodes.
    """
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
    """
    Ensure block children are not empty; add empty text if needed.

    Args:
        block (SlateBlockItem): The block to process.

    Returns:
        SlateBlockItem: The processed block.
    """
    if block.get("children") == []:
        block["children"] = [wrap_text("")]
    return block


def _get_id() -> str:
    """
    Generate a random string ID for table blocks.

    Returns:
        str: The generated ID.
    """
    id_ = math.floor(random() * math.exp2(24))  # noQA: S311
    return f"{id_}"


def table(
    rows: list[dict | str],
    css_classes: list[str],
    hide_headers: bool = False,
) -> dict:
    """
    Construct a table block from rows and CSS classes.

    Args:
        rows (list[dict | str]): The table rows.
        css_classes (list[str]): CSS classes for styling.
        hide_headers (bool, optional): Whether to hide headers. Defaults to ``False``.

    Returns:
        dict: The table block.
    """
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
    """
    Construct a table row block from cells.

    Args:
        cells (list[SlateBlockItem]): The row cells.

    Returns:
        SlateBlockItem: The table row block.
    """
    return {
        "key": _get_id(),
        "cells": cells,
    }


def table_cell(cell_type: str, value: t.SlateBlockItem) -> t.SlateBlockItem:
    """
    Construct a table cell block.

    Args:
        cell_type (str): The cell type (``header`` or ``data``).
        value (SlateBlockItem): The cell value.

    Returns:
        SlateBlockItem: The table cell block.
    """
    return {
        "key": _get_id(),
        "type": cell_type,
        "value": value,
    }


def invalid_subblock(block: t.SlateBlockItem | t.VoltoBlock) -> bool:
    """
    Check if a block should not be a child of a Slate block.

    Args:
        block (SlateBlockItem | VoltoBlock): The block to check.

    Returns:
        bool: ``True`` if invalid, ``False`` otherwise.
    """
    type_ = block.get("@type", "")
    return bool(type_)

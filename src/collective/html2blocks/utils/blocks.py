"""
Utility functions for Volto block detection and layout construction.

This module provides helpers for identifying Volto blocks and assembling
block layout information for use in Volto-based content management systems.

Example:
    .. code-block:: python

        from collective.html2blocks.utils import blocks

        block = {"@type": "slate", "value": [...], ...}
        blocks.info_from_blocks([block])
"""

from collective.html2blocks import _types as t
from uuid import uuid4


def is_volto_block(block: t.VoltoBlock | t.SlateBlockItem) -> bool:
    """
    Check if the given block is a Volto block.

    A Volto block is identified by the presence of the ``@type`` key.

    Args:
        block (VoltoBlock | SlateBlockItem): The block to check.

    Returns:
        bool: True if the block is a Volto block, False otherwise.

    Example:
        .. code-block:: pycon

            >>> is_volto_block({"@type": "slate", "value": []})
            True
            >>> is_volto_block({"type": "p", "children": []})
            False
    """
    return bool(block.get("@type"))


def info_from_blocks(raw_blocks: list[t.VoltoBlock]) -> t.VoltoBlocksInfo:
    """
    Construct Volto blocks info and layout from a list of blocks.

    This function generates unique IDs for each block and assembles them into
    the Volto blocks structure, including the layout order.

    Args:
        raw_blocks (list[VoltoBlock]): List of Volto blocks to include.

    Returns:
        VoltoBlocksInfo: Dictionary with 'blocks' and 'blocks_layout' keys.

    Example:
        .. code-block:: pycon

            >>> blocks = [{"@type": "slate", "value": []}]
            >>> info = info_from_blocks(blocks)
            >>> print(info)
            {'blocks': {'...uuid...': {...}}, 'blocks_layout': {'items': ['...uuid...']}}
    """  # noqa: E501
    blocks = {str(uuid4()): block for block in raw_blocks}
    layout = list(blocks.keys())
    return {"blocks": blocks, "blocks_layout": {"items": layout}}

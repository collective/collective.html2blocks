"""
Slate block converter for collective.html2blocks.

This module provides the default block converter for rich text elements,
transforming paragraphs, headings, lists, and other inline/nested content into
Volto Slate blocks. It uses the parser to deserialize HTML elements and
normalizes the result for Volto consumption.

Implementation details:
- Handles plain text extraction and normalization.
- Supports nested and inline content, grouping and flattening as needed.
- Yields Volto Slate blocks and any additional blocks found during parsing.

Example usage::

    from collective.html2blocks.blocks.slate import slate_block
    blocks = list(slate_block(element))
"""

from . import parser
from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate as utils


@registry.default_converter
def slate_block(
    element: t.Tag,
) -> Generator[t.VoltoBlock, None, t.VoltoBlock | None]:
    """
    Convert rich text HTML elements to Volto Slate blocks.

    This converter deserializes paragraphs, headings, lists, and other content
    into Volto Slate blocks, handling nested and inline elements, and normalizing
    the result for Volto. Additional blocks found during parsing are also yielded.

    Args:
        element (Tag): The HTML element to convert.

    Yields:
        VoltoBlock: The converted Slate block and any additional blocks.

    Example::

        blocks = list(slate_block(element))
        # [{'@type': 'slate', 'plaintext': ..., 'value': [...]}]
    """
    plaintext = markup.extract_plaintext(element)
    value = yield from parser.deserialize(element)
    blocks: list[t.VoltoBlock] = []
    additional_blocks: list[t.VoltoBlock] = []
    if value is None:
        value = []
    elif isinstance(value, list):
        value = yield from parser.extract_blocks(value)
    elif isinstance(value, dict) and (children := value.get("children", [])):
        children = yield from parser.extract_blocks(children)
        value["children"] = children
    if value and not blocks:
        value = [value] if not isinstance(value, list) else value
        value = utils.process_top_level_items(value)
        block = {"@type": "slate", "plaintext": plaintext, "value": value}
        block = yield from parser.finalize_slate(block)
        blocks = [block]
    yield from blocks
    yield from additional_blocks
    return None

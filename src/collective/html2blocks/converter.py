"""
Conversion utilities for transforming HTML into Volto blocks.

This module provides functions to convert HTML markup into Volto blocks and
assemble them into Volto's block layout structure. It is used as the main
conversion engine for the collective.html2blocks package.

Example usage::

    from collective.html2blocks.converter import html_to_blocks, volto_blocks

    html = "<p>Hello <strong>world</strong>!</p>"
    blocks = html_to_blocks(html)
    info = volto_blocks(html)

"""

from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks._types import VoltoBlocksInfo
from collective.html2blocks.utils import blocks
from collective.html2blocks.utils import markdown
from collective.html2blocks.utils import markup
from typing import Literal


SourceFormat = Literal["html", "markdown"]


def html_to_blocks(source: str) -> list[t.VoltoBlock]:
    """
    Convert HTML source into a list of Volto blocks.

    This function parses the given HTML string and converts its block-level elements
    into Volto blocks using registered block converters. It is the main entry point
    for extracting block data from HTML markup.

    Args:
        source (str): The HTML content to convert.

    Returns:
        list[VoltoBlock]: List of Volto blocks extracted from the HTML.

    Example::

        >>> html = "<h1>Title</h1><p>Paragraph</p>"
        >>> html_to_blocks(html)
        [{"@type": "slate", ...}, ...]

    """
    block_level_tags = registry.elements_with_block_converters()
    soup = markup.parse_source(source, block_level_tags=block_level_tags)
    response = []
    elements = markup.all_children(soup)
    for element in elements:
        block_converter = registry.get_block_converter(element, strict=False)
        if block_converter and (el_blocks := block_converter(element)):
            response.extend(el_blocks)
    return response


def markdown_to_blocks(source: str) -> list[t.VoltoBlock]:
    """
    Convert Markdown source into a list of Volto blocks.

    The Markdown is rendered to HTML, and the HTML is then converted with
    :func:`html_to_blocks`, so every block converter applies unchanged.

    Args:
        source (str): The Markdown content to convert.

    Returns:
        list[VoltoBlock]: List of Volto blocks extracted from the Markdown.

    Example::

        >>> markdown_to_blocks("# Title\\n\\nParagraph")
        [{"@type": "slate", ...}, ...]

    """
    return html_to_blocks(markdown.markdown_to_html(source))


def volto_blocks(
    source: str,
    default_blocks: list[t.VoltoBlock] | None = None,
    additional_blocks: list[t.VoltoBlock] | None = None,
    source_format: SourceFormat = "html",
) -> VoltoBlocksInfo:
    """
    Convert HTML or Markdown source into a Volto blocks info structure with layout.

    This function parses the source, converts it to Volto blocks, and assembles
    the result into a VoltoBlocksInfo dictionary containing both the blocks and
    their layout order. Optionally, you can prepend or append blocks to the result.

    Args:
        source (str): The HTML or Markdown content to convert.
        default_blocks (list[VoltoBlock], optional): Blocks to include before
                                                     the converted blocks.
        additional_blocks (list[VoltoBlock], optional): Blocks to include after
                                                        the converted blocks.
        source_format (str, optional): Format of ``source``, either ``"html"``
                                       (default) or ``"markdown"``.

    Returns:
        VoltoBlocksInfo: Dictionary with 'blocks' and 'blocks_layout' keys.

    Raises:
        ValueError: If ``source_format`` is not ``"html"`` or ``"markdown"``.

    Example::

        >>> html = "<h1>Title</h1><p>Paragraph</p>"
        >>> volto_blocks(html)
        {
            "blocks": {"block-id-1": {...}, ...},
            "blocks_layout": {"items": ["block-id-1", ...]}
        }
    """
    match source_format:
        case "html":
            converted = html_to_blocks(source)
        case "markdown":
            converted = markdown_to_blocks(source)
        case _:
            raise ValueError(f"Unsupported source format: {source_format}")
    blocks_ = default_blocks.copy() if default_blocks else []
    for block in converted:
        blocks_.append(block)
    if additional_blocks:
        blocks_.extend(additional_blocks)
    return blocks.info_from_blocks(blocks_)

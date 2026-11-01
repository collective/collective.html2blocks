"""
Conversion utilities for transforming HTML into Volto blocks.

This module provides functions to convert HTML markup into Volto blocks and
assemble them into Volto's block layout structure. It is used as the main
conversion engine for the collective.html2blocks package.

The default ``slate`` converter produces one Volto block per element. The
``plate`` converter migrates that result to the single ``__somersault__`` block
of Plone Aurora, and :func:`slate_to_plate` does the same for existing content.

Example usage::

    from collective.html2blocks.converter import html_to_blocks, volto_blocks

    html = "<p>Hello <strong>world</strong>!</p>"
    blocks = html_to_blocks(html)
    info = volto_blocks(html)

"""

from collections.abc import Mapping
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks._types import VoltoBlocksInfo
from collective.html2blocks.utils import blocks as blocks_utils
from collective.html2blocks.utils import markdown
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import plate
from typing import Any
from typing import Literal


SourceFormat = Literal["html", "markdown"]
ConverterName = Literal["slate", "plate"]

CONVERTERS: tuple[ConverterName, ...] = ("slate", "plate")


def _check_converter(converter: str) -> None:
    """Raise ``ValueError`` for a converter that doesn't exist."""
    if converter not in CONVERTERS:
        raise ValueError(f"Unsupported converter: {converter}")


def _plate_setting(blocks: t.BlocksSetting | None) -> t.BlocksSetting:
    """
    Return the ``blocks`` setting of a conversion to Plate.

    Aurora has native code blocks, and the ``codeBlock`` converter is the one that
    keeps the lines and the language of a ``<pre>``, so it's on unless disabled.

    :param blocks: The ``blocks`` setting of the caller.
    :returns: The setting with ``codeBlock`` enabled, if it doesn't mention it.
    """
    return {plate.CODE_BLOCK_TYPE: True, **(blocks or {})}


def html_to_blocks(
    source: str,
    *,
    blocks: t.BlocksSetting | None = None,
    converter: ConverterName = "slate",
    title: str = "",
) -> list[t.VoltoBlock]:
    """
    Convert HTML source into a list of Volto blocks.

    This function parses the given HTML string and converts its block-level elements
    into Volto blocks using registered block converters. It is the main entry point
    for extracting block data from HTML markup.

    :param source: The HTML content to convert.
    :param blocks: Enables, disables and configures block types, keyed by their
        Volto ``@type``: ``True`` or a dict of options enables a block, ``False``
        disables it (see :func:`~collective.html2blocks.registry.resolve_blocks`).
        Block types left out keep their default state.
    :param converter: ``"slate"`` (default) for one block per element, or ``"plate"``
        for a list with the ``__somersault__`` block of Plone Aurora.
    :param title: The title of the content, used with ``"plate"`` for a ``title``
        block. :func:`html_to_blocks` itself produces no ``title`` block, but
        :func:`volto_blocks` accepts one in ``default_blocks``.
    :returns: List of Volto blocks extracted from the HTML.
    :raises ValueError: For an unknown converter, or an unknown block type or option
        in ``blocks``.

    Example::

        >>> html = "<h1>Title</h1><p>Paragraph</p>"
        >>> html_to_blocks(html)
        [{"@type": "slate", ...}, ...]

    """
    _check_converter(converter)
    if converter == "plate":
        blocks = _plate_setting(blocks)
    with registry.conversion(blocks):
        block_level_tags = registry.elements_with_block_converters()
        soup = markup.parse_source(source, block_level_tags=block_level_tags)
        response = []
        elements = markup.all_children(soup)
        for element in elements:
            block_converter = registry.get_block_converter(element, strict=False)
            if block_converter and (el_blocks := block_converter(element)):
                response.extend(el_blocks)
    if converter == "plate":
        return [plate.somersault_block(plate.value_from_blocks(response, title))]
    return response


def markdown_to_blocks(
    source: str,
    *,
    blocks: t.BlocksSetting | None = None,
    converter: ConverterName = "slate",
    title: str = "",
) -> list[t.VoltoBlock]:
    """
    Convert Markdown source into a list of Volto blocks.

    The Markdown is rendered to HTML, and the HTML is then converted with
    :func:`html_to_blocks`, so every block converter applies unchanged.

    :param source: The Markdown content to convert.
    :param blocks: Enables, disables and configures block types, see
        :func:`html_to_blocks`.
    :param converter: ``"slate"`` (default) or ``"plate"``, see
        :func:`html_to_blocks`.
    :param title: The title of the content, see :func:`html_to_blocks`.
    :returns: List of Volto blocks extracted from the Markdown.
    :raises ValueError: For an unknown converter, or an unknown block type or option
        in ``blocks``.

    Example::

        >>> markdown_to_blocks("# Title\\n\\nParagraph")
        [{"@type": "slate", ...}, ...]

    """
    return html_to_blocks(
        markdown.markdown_to_html(source),
        blocks=blocks,
        converter=converter,
        title=title,
    )


def volto_blocks(
    source: str,
    default_blocks: list[t.VoltoBlock] | None = None,
    additional_blocks: list[t.VoltoBlock] | None = None,
    source_format: SourceFormat = "html",
    *,
    blocks: t.BlocksSetting | None = None,
    converter: ConverterName = "slate",
    title: str = "",
) -> VoltoBlocksInfo:
    """
    Convert HTML or Markdown source into a Volto blocks info structure with layout.

    This function parses the source, converts it to Volto blocks, and assembles
    the result into a VoltoBlocksInfo dictionary containing both the blocks and
    their layout order. Optionally, you can prepend or append blocks to the result.

    :param source: The HTML or Markdown content to convert.
    :param default_blocks: Blocks to include before the converted blocks.
    :param additional_blocks: Blocks to include after the converted blocks.
    :param source_format: Format of ``source``, either ``"html"`` (default) or
        ``"markdown"``.
    :param blocks: Enables, disables and configures block types, see
        :func:`html_to_blocks`.
    :param converter: ``"slate"`` (default) keeps one block per element. ``"plate"``
        puts ``default_blocks``, the converted blocks and ``additional_blocks`` in
        the ``__somersault__`` block of Plone Aurora, its only block.
    :param title: The title of the content, used with ``"plate"`` for a ``title``
        block in ``default_blocks`` or ``additional_blocks``.
    :returns: Dictionary with ``blocks`` and ``blocks_layout`` keys.
    :raises ValueError: If ``source_format`` is not ``"html"`` or ``"markdown"``,
        for an unknown converter, or for an unknown block type or option in
        ``blocks``.

    Example::

        >>> html = "<h1>Title</h1><p>Paragraph</p>"
        >>> volto_blocks(html, blocks={"codeBlock": True})
        {
            "blocks": {"block-id-1": {...}, ...},
            "blocks_layout": {"items": ["block-id-1", ...]}
        }
    """
    _check_converter(converter)
    if converter == "plate":
        blocks = _plate_setting(blocks)
    match source_format:
        case "html":
            converted = html_to_blocks(source, blocks=blocks)
        case "markdown":
            converted = markdown_to_blocks(source, blocks=blocks)
        case _:
            raise ValueError(f"Unsupported source format: {source_format}")
    blocks_ = default_blocks.copy() if default_blocks else []
    for block in converted:
        blocks_.append(block)
    if additional_blocks:
        blocks_.extend(additional_blocks)
    if converter == "plate":
        return plate.info_from_blocks(blocks_, title)
    return blocks_utils.info_from_blocks(blocks_)


def slate_to_plate(
    content: Mapping[str, Any], title: str | None = None
) -> dict[str, Any]:
    """
    Add the ``__somersault__`` block of Plone Aurora to an existing content item.

    The migration is additive and idempotent, see
    :func:`~collective.html2blocks.utils.plate.migrate_content`.

    :param content: A content item with ``blocks`` and ``blocks_layout`` keys.
    :param title: The title for a ``title`` block. Defaults to the ``title`` key of
        the content item.
    :returns: A copy of the content item with the ``__somersault__`` block.

    Example::

        >>> content = {
        ...     "title": "Welcome",
        ...     "blocks": {"a": {"@type": "title"}},
        ...     "blocks_layout": {"items": ["a"]},
        ... }
        >>> slate_to_plate(content)["blocks"]["__somersault__"]["value"][0]["type"]
        'title'

    """
    return plate.migrate_content(content, title)

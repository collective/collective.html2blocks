"""
Image block converter for collective.html2blocks.

This module provides the block converter for <img> elements, transforming them
into Volto image blocks. It extracts image attributes, alignment, size, and
custom data attributes, supporting Plone/Volto conventions for image handling.

Implementation details:
- Alignment and size are inferred from CSS classes and image src patterns.
- Custom data attributes are added to the block for extensibility.
- The converter yields a Volto image block with all relevant metadata.

Example usage::

    from collective.html2blocks.blocks.image import image_block
    blocks = list(image_block(element))
"""

from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.logger import logger

import re


def _align_from_classes(css_classes: list[str]) -> str:
    align = "center"
    if "image-left" in css_classes:
        align = "left"
    elif "image-right" in css_classes:
        align = "right"
    elif "image-inline" in css_classes:
        align = "center"
    return align


def _add_align_to_block(block: t.VoltoBlock, css_classes: list[str]) -> None:
    size: str = "l"
    match align := _align_from_classes(css_classes):
        case "left":
            size = "m"
        case "right":
            size = "m"
    block["align"] = align
    block["size"] = size


def _add_size_to_block(block: t.VoltoBlock, src: str) -> None:
    size: str = block.get("size", "m")
    match _scale_from_src(src):
        case "large":
            size = "l"
        case "preview":
            size = "l"
        case "thumb":
            size = "s"
        case "tile":
            size = "s"
    block["size"] = size


def _add_data_attrs_to_block(block: t.VoltoBlock, attrs: dict) -> None:
    data_attrs: dict = {k: v for k, v in attrs.items() if k.startswith("data-")}
    for raw_key, value in data_attrs.items():
        key = raw_key.replace("data-", "")
        block[key] = value


def _scale_from_src(src: str) -> str:
    scale = ""
    if (match := re.search("/@@images/(?P<field>[^/]*)/(?P<scale>.+)", src)) or (
        match := re.search("/image_(?P<scale>.+)", src)
    ):
        scale = match.group("scale")
    elif match := re.search("/image$", src):
        scale = "original"
    return scale


@registry.block_converter("img")
def image_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """
    Convert an <img> element to a Volto image block.

    This converter extracts src, alt, title, alignment, size, and custom data
    attributes from the image element and yields a Volto image block.

    Args:
        element (Tag): The <img> element to convert.

    Yields:
        VoltoBlock: The converted image block.

    Example::

        blocks = list(image_block(element))
        # [{'@type': 'image', 'url': ..., 'alt': ..., ...}]
    """
    src: str = element.get("src")
    if src is None:
        logger.debug(f"Dropping element {element}")
        return None
    url: str = src.split("/@@images")[0]
    css_classes: list[str] = element.get("class", [])
    alt: str = element.get("alt", "")
    title: str = element.get("title", "")
    block: t.VoltoBlock = {"@type": "image", "url": url, "alt": alt, "title": title}
    _add_align_to_block(block, css_classes)
    _add_size_to_block(block, src)
    _add_data_attrs_to_block(block, element.attrs)
    yield block

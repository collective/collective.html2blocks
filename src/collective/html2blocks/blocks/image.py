from collective.html2blocks import registry
from collective.html2blocks._types import Element

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


def _add_align_to_block(block: dict, css_classes: list[str]) -> None:
    size: str = "l"
    match align := _align_from_classes(css_classes):
        case "left":
            size = "m"
        case "right":
            size = "m"
    block["align"] = align
    block["size"] = size


def _add_size_to_block(block: dict, src: str) -> None:
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


def _add_data_attrs_to_block(block: dict, attrs: dict) -> None:
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
def image_block(element: Element) -> list[dict]:
    """Given an image, return an image block."""
    src: str = element["src"]
    url: str = src.split("/@@images")[0]
    css_classes: list[str] = element.get("class", [])
    alt: str = element.get("alt", "")
    title: str = element.get("title", "")
    block = {"@type": "image", "url": url, "alt": alt, "title": title}
    _add_align_to_block(block, css_classes)
    _add_size_to_block(block, src)
    _add_data_attrs_to_block(block, element.attrs)
    return [block]

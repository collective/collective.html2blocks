from bs4 import Tag
from bs4.element import PageElement as Element
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict

import re


@dataclass
class IFrameConverter:
    url_pattern: str
    provider: str
    converter: Callable


@dataclass
class Registry:
    block_converters: dict[str, Callable]
    element_converters: dict[str, dict[Callable, str]]
    iframe_converters: dict[re.Pattern, IFrameConverter]
    default: Callable | None = None


VoltoBlock = TypedDict("VoltoBlock", {"@type": str})


class BlocksLayout(TypedDict):
    """Blocks layout information."""

    items: list[str]


class VoltoBlocksInfo(TypedDict):
    """Volto Blocks information."""

    blocks: dict[str, VoltoBlock]
    blocks_layout: BlocksLayout


@dataclass
class EmbedInfo:
    url: str
    provider_id: str
    converter: Callable


__all__ = ["Element", "EmbedInfo", "Registry", "Tag", "VoltoBlock", "VoltoBlocksInfo"]

from bs4 import PageElement as Element
from bs4 import Tag
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


class VoltoBlocksInfo(TypedDict):
    """Volto Blocks information."""

    blocks: dict[str, dict]
    blocks_layout: dict[str, list]


@dataclass
class EmbedInfo:
    url: str
    provider_id: str
    converter: Callable


__all__ = ["Element", "EmbedInfo", "Registry", "Tag", "VoltoBlock", "VoltoBlocksInfo"]

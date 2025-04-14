from bs4 import PageElement as Element
from bs4 import Tag
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Registry:
    block_converters: dict[str, callable]
    element_converters: dict[str, dict[callable, str]]
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
    provider: str


__all__ = ["Element", "EmbedInfo", "Registry", "Tag", "VoltoBlock", "VoltoBlocksInfo"]

from bs4 import PageElement as Element
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


__all__ = ["Element", "Registry", "VoltoBlock", "VoltoBlocksInfo"]

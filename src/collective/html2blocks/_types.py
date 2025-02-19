from bs4 import PageElement as Element
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Registry:
    block_converters: dict[str, callable]
    element_converters: dict[str, dict[callable, str]]
    default: Callable | None = None


__all__ = ["Element", "Registry"]

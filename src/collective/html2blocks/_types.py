from bs4 import Tag
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Sequence
from dataclasses import dataclass
from typing import NotRequired
from typing import Protocol
from typing import TypedDict

import re


BaseVoltoBlock = TypedDict("BaseVoltoBlock", {"@type": str})


class VoltoBlock(BaseVoltoBlock, total=False):
    """Volto Block type with optional fields."""

    value: NotRequired[list]
    align: NotRequired[str]
    size: NotRequired[str]
    url: NotRequired[str]


class SlateBlockItem(TypedDict, total=False):
    """A child in an Slate Block."""

    type: NotRequired[str]
    text: NotRequired[str]
    key: NotRequired[str]
    cells: NotRequired[Sequence["SlateBlockItem"]]
    children: NotRequired[list["SlateBlockItem"]]
    value: NotRequired["SlateBlockItem | str"]


class BlocksLayout(TypedDict):
    """Blocks layout information."""

    items: Sequence[str]


class VoltoBlocksInfo(TypedDict):
    """Volto Blocks information."""

    blocks: dict[str, VoltoBlock]
    blocks_layout: BlocksLayout


class BlockConverter(Protocol):
    """Protocol for block converters."""

    __name__: str
    __orig_mod__: str

    def __call__(self, element: Tag) -> Generator[VoltoBlock, None, None]: ...


class ElementConverterFunc(Protocol):
    """Protocol for element converters."""

    __name__: str
    __module__: str

    def __call__(
        self, element: Tag, tag_name: str
    ) -> Generator[VoltoBlock, None, SlateBlockItem]: ...


class ElementConverter(ElementConverterFunc):
    """Protocol for element converters."""

    __name__: str
    __orig_mod__: str


SlateItemsGenerator = Generator[VoltoBlock | None, None, list[SlateBlockItem]]

SlateItemGenerator = Generator[VoltoBlock | None, None, SlateBlockItem | None]


@dataclass
class IFrameConverter:
    url_pattern: str
    provider: str
    converter: Callable


@dataclass
class Registry:
    block_converters: dict[str, BlockConverter]
    element_converters: dict[str, ElementConverter]
    iframe_converters: dict[re.Pattern | str, IFrameConverter]
    default: BlockConverter | None = None


@dataclass
class EmbedInfo:
    url: str
    provider_id: str
    converter: Callable


class ReportRegistrations(TypedDict):
    """Report registrations type."""

    block: dict[str, str]
    element: dict[str, str]
    iframe: dict[str, str]


__all__ = [
    "EmbedInfo",
    "Registry",
    "ReportRegistrations",
    "Tag",
    "VoltoBlock",
    "VoltoBlocksInfo",
]

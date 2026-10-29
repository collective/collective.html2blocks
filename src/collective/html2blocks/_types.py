from bs4 import Tag
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import NotRequired
from typing import Protocol
from typing import TypedDict

import re


BaseVoltoBlock = TypedDict("BaseVoltoBlock", {"@type": str})


class VoltoBlock(BaseVoltoBlock, total=False):
    """Volto Block type with optional fields."""

    # Each block type has its own keys (``table``, ``src``, ``code``...). Without
    # this, pydantic (in the HTTP service) drops every key not declared here.
    # A plain dict, so pydantic stays an optional dependency. Not annotated: in a
    # TypedDict, an annotation (even ClassVar) would declare a key.
    __pydantic_config__ = {"extra": "allow"}  # type: ignore[misc]  # noqa: RUF012

    value: NotRequired[list]
    align: NotRequired[str]
    size: NotRequired[str]
    url: NotRequired[str]
    plaintext: NotRequired[str]


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
    block_type: str = ""


@dataclass
class BlockType:
    """
    A Volto block type the converters can produce.

    :ivar name: The Volto ``@type`` of the block.
    :ivar package: The frontend package that provides the block.
    :ivar enabled: Whether the block is produced when no setting mentions it.
    :ivar required: Whether the block can be disabled at all.
    :ivar options: Dataclass with the options of the block and their defaults.
    :ivar description: One line describing what the block is produced from.
    :ivar tags: HTML tags converted into this block.
    :ivar providers: Iframe providers converted into this block.
    :ivar fallback: Block converter used for its tags while the block is disabled.
        Without one, the tags are converted as if they had no block converter.
    """

    name: str
    package: str
    enabled: bool = True
    required: bool = False
    options: type | None = None
    description: str = ""
    tags: list[str] = field(default_factory=list)
    providers: list[str] = field(default_factory=list)
    fallback: BlockConverter | None = None


# Value of one entry of the ``blocks`` setting: ``True`` or a dict of options
# enables the block, ``False`` disables it.
BlockSetting = bool | dict[str, Any]

BlocksSetting = Mapping[str, BlockSetting]


@dataclass(frozen=True)
class ResolvedBlocks:
    """
    The ``blocks`` setting of a conversion, validated and merged with the defaults.

    :ivar enabled: Names of the enabled block types.
    :ivar options: Options of each enabled block type that declares options.
    """

    enabled: frozenset[str]
    options: Mapping[str, Any]


@dataclass
class Registry:
    block_converters: dict[str, BlockConverter]
    element_converters: dict[str, ElementConverter]
    iframe_converters: dict[re.Pattern | str, IFrameConverter]
    default: BlockConverter | None = None
    block_types: dict[str, BlockType] = field(default_factory=dict)
    # Block type produced by the block converter of each tag.
    tag_block_types: dict[str, str] = field(default_factory=dict)


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


class BlockOptionReport(TypedDict):
    """One option of a block type in :class:`BlockReport`."""

    name: str
    type: str
    default: Any


class BlockReport(TypedDict):
    """Report of one block type, see ``registry.report_blocks``."""

    block_type: str
    package: str
    description: str
    enabled: bool
    required: bool
    tags: list[str]
    providers: list[str]
    options: list[BlockOptionReport]
    fallback: str


__all__ = [
    "BlockOptionReport",
    "BlockReport",
    "BlockSetting",
    "BlockType",
    "BlocksSetting",
    "EmbedInfo",
    "Registry",
    "ReportRegistrations",
    "ResolvedBlocks",
    "Tag",
    "VoltoBlock",
    "VoltoBlocksInfo",
]

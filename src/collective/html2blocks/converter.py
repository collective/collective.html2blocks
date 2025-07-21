from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks._types import VoltoBlocksInfo
from collective.html2blocks.utils import blocks
from collective.html2blocks.utils import markup


def html_to_blocks(source: str) -> list[t.VoltoBlock]:
    """Convert from html source."""
    block_level_tags = registry.elements_with_block_converters()
    soup = markup.parse_source(source, block_level_tags=block_level_tags)
    response = []
    elements = markup.all_children(soup)
    for element in elements:
        block_converter = registry.get_block_converter(element, strict=False)
        if block_converter and (el_blocks := block_converter(element)):
            response.extend(el_blocks)
    return response


def volto_blocks(
    source: str,
    default_blocks: list[t.VoltoBlock] | None = None,
    additional_blocks: list[t.VoltoBlock] | None = None,
) -> VoltoBlocksInfo:
    """Return volto blocks information."""
    blocks_ = default_blocks.copy() if default_blocks else []
    for block in html_to_blocks(source):
        blocks_.append(block)
    if additional_blocks:
        blocks_.extend(additional_blocks)
    return blocks.info_from_blocks(blocks_)

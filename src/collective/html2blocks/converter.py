from collective.html2blocks import registry
from collective.html2blocks._types import VoltoBlocksInfo
from collective.html2blocks.utils import blocks
from collective.html2blocks.utils import markup


def html_to_blocks(source: str) -> list[dict]:
    """Convert from html source."""
    soup = markup.parse_source(source)
    response = []
    elements = markup.all_children(soup)
    for element in elements:
        block_converter = registry.get_block_converter(element, strict=False)
        el_blocks = block_converter(element)
        if el_blocks:
            response.extend(el_blocks)
    return response


def volto_blocks(
    source: str, default_blocks: list[dict] | None = None
) -> VoltoBlocksInfo:
    """Return volto blocks information."""
    blocks_ = default_blocks.copy() if default_blocks else []
    for block in html_to_blocks(source):
        blocks_.append(block)
    return blocks.info_from_blocks(blocks_)

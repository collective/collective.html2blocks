from collective.html2blocks import registry
from collective.html2blocks.utils import markup


def html_to_blocks(source: str) -> list[dict]:
    """Convert from html source."""
    soup = markup.parse_source(source)
    response = []
    elements = markup.all_children(soup)
    for element in elements:
        block_converter = registry.get_block_converter(element, strict=False)
        blocks = block_converter(element)
        if blocks:
            response.extend(blocks)
    return response

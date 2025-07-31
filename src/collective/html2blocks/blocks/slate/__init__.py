from . import parser
from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate as utils


@registry.default_converter
def slate_block(
    element: t.Tag,
) -> Generator[t.VoltoBlock, None, t.VoltoBlock | None]:
    plaintext = markup.extract_plaintext(element)
    value = yield from parser.deserialize(element)
    blocks: list[t.VoltoBlock] = []
    additional_blocks: list[t.VoltoBlock] = []
    if value is None:
        value = []
    elif isinstance(value, list):
        value = yield from parser.extract_blocks(value)
    elif isinstance(value, dict) and (children := value.get("children", [])):
        children = yield from parser.extract_blocks(children)
        value["children"] = children
    if value and not blocks:
        value = [value] if not isinstance(value, list) else value
        value = utils.process_top_level_items(value)
        block = {"@type": "slate", "plaintext": plaintext, "value": value}
        block = yield from parser.finalize_slate(block)
        blocks = [block]
    yield from blocks
    yield from additional_blocks
    return None

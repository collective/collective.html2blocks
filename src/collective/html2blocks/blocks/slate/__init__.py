from . import parser
from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.utils import blocks as butils
from collective.html2blocks.utils import markup


@registry.default_converter
def slate_block(element: Element) -> list[VoltoBlock]:
    plaintext = markup.extract_plaintext(element)
    value = parser.deserialize(element)
    blocks = []
    additional_blocks = []
    if value is None:
        value = []
    elif isinstance(value, list):
        value, additional_blocks = parser.extract_blocks(value)
    elif isinstance(value, dict) and (children := value.get("children", [])):
        children, additional_blocks = parser.extract_blocks(children)
        value["children"] = children
    elif isinstance(value, dict) and butils.is_volto_block(value):
        # Return block information if it was processed somewhere else
        # in the codebase
        blocks = [value]
    if value and not isinstance(value, list):
        value = [value]
    if value and not blocks:
        block = {"@type": "slate", "plaintext": plaintext, "value": value}
        blocks = parser.finalize_slate(block)
    blocks.extend(additional_blocks)
    return blocks

from . import parser
from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks.utils import markup


def _extract_blocks(raw_children: list[dict]) -> tuple[list[dict], list[dict]]:
    children = []
    blocks = []
    for child in raw_children:
        if isinstance(child, dict) and child.get("@type", ""):
            blocks.append(child)
        else:
            children.append(child)
    return children, blocks


@registry.default_converter
def slate_block(element: Element) -> list[dict]:
    plaintext = markup.extract_plaintext(element)
    value = parser.deserialize(element)
    blocks = []
    additional_blocks = []
    if value is None:
        value = []
    elif isinstance(value, list):
        value, additional_blocks = _extract_blocks(value)
    elif isinstance(value, dict) and (children := value.get("children", [])):
        children, additional_blocks = _extract_blocks(children)
        value["children"] = children
    elif isinstance(value, dict) and value.get("@type", ""):
        # Return block information if it was processed somewhere else
        # in the codebase
        blocks = [value]
    if value and not isinstance(value, list):
        value = [value]
    if value and not blocks:
        blocks = [{"@type": "slate", "plaintext": plaintext, "value": value}]
    blocks.extend(additional_blocks)
    return blocks

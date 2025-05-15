from bs4 import Comment
from bs4.element import NavigableString
from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.logger import logger
from collective.html2blocks.utils import blocks as butils
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate


def extract_blocks(raw_children: list[dict]) -> tuple[list[dict], list[VoltoBlock]]:
    raw_children = raw_children if raw_children else []
    children = []
    blocks = []
    for child in raw_children:
        if isinstance(child, dict) and butils.is_volto_block(child):
            blocks.append(child)
        else:
            children.append(child)
    return children, blocks


def _instropect_children(child: dict) -> tuple[list[dict], list[VoltoBlock]]:
    blocks = []
    children = []
    if child and "children" in child:
        children, sub_blocks = extract_blocks(child["children"])
        blocks.extend(sub_blocks)
        child["children"] = children
    return child, blocks


def finalize_slate(block: VoltoBlock) -> list[VoltoBlock]:
    """Check if slate has invalid children blocks."""
    blocks = []
    value = []
    for item in block["value"]:
        if not item:
            continue
        child, sub_blocks = _instropect_children(item)
        value.append(child)
        if sub_blocks:
            blocks.extend(sub_blocks)
    block["value"] = value
    if blocks:
        blocks.insert(0, block)
    else:
        blocks = [block]
    return blocks


def _handle_only_child(child: Element, styles: dict | None = None) -> dict:
    text = child.text
    styles = styles if styles else {}
    if not text.strip():
        return slate.wrap_text(" ")
    elif block_converter := registry.get_block_converter(child):
        return block_converter(child)
    elif element_converter := registry.get_element_converter(child):
        return element_converter(child)
    return slate.wrap_text(text)


def _handle_block_(element: Element, tag_name: str) -> dict:
    block_children: list = deserialize_children(element)
    total_children = len(block_children)
    first_child = block_children[0] if total_children else None
    if total_children == 1:
        if butils.is_volto_block(first_child):
            # Check if we already have a block information
            return first_child
        child_type = first_child.get("type")
        if tag_name in ("p", "blockquote") and child_type == "p":
            block_children = first_child["children"]
    if len(block_children) == 1 and butils.is_volto_block(first_child):
        return first_child
    response = {
        "type": tag_name,
    }
    if tag_name in ("td", "th") and block_children and isinstance(first_child, str):
        block_children = [slate.wrap_paragraph(slate.wrap_text(first_child, True))]
    if slate.has_internal_block(block_children):
        internal_children = slate.normalize_block_nodes(block_children, tag_name)
        if (
            len(internal_children) == 1
            and internal_children[0]["type"] == response["type"]
        ):
            block_children = internal_children[0]["children"]
        elif len(internal_children) > 1:
            block_children = internal_children
    if tag_name == "p" and "callout" in markup.css_classes(element):
        response["type"] = "callout"
    response["children"] = block_children
    return slate.process_children(response)


@registry.element_converter(["hr"], "p")
def _hr_(element: Element, tag_name: str) -> dict:
    return {"type": tag_name, "children": slate.wrap_text("", True)}


@registry.element_converter(["body"])
def _body_(element: Element, tag_name: str) -> dict:
    """Deserialize body tag."""
    return {"children": deserialize_children(element)}


@registry.element_converter(["h1", "h2", "h3", "h4", "h5", "h6"])
def _header_(element: Element, tag_name: str) -> dict:
    block = _handle_block_(element, tag_name)
    if slate.invalid_subblock(block):
        return block
    response = block
    valid_subblocks = []
    invalid_subblocks = []
    for child in block["children"]:
        if slate.invalid_subblock(child):
            invalid_subblocks.append(child)
        else:
            valid_subblocks.append(child)
    if invalid_subblocks:
        block["children"] = valid_subblocks
        response = [block, *invalid_subblocks]
    return response


@registry.element_converter(["b", "strong"], "strong")
def _strong_(element: Element, tag_name: str) -> dict:
    """Deserialize b and strong tags."""
    return {"type": tag_name, "children": deserialize_children(element)}


@registry.element_converter(["code"], "code")
def _code_(element: Element, tag_name: str) -> dict:
    """Deserialize Code Block."""
    # CHECK
    text = element.text
    return {"type": tag_name, "text": text}


@registry.element_converter(["div"], "div")
def _div_(element: Element, tag_name: str) -> dict:
    """Deserialize a div block."""
    styles = markup.styles(element)
    children = markup.all_children(element)
    block = {}
    if len(children) == 1:
        child = children[0]
        block = _handle_only_child(child, styles)
        block = slate.wrap_paragraph([block]) if slate.is_simple_text(block) else block
    else:
        block_children = []
        for child in children:
            if isinstance(child, NavigableString):
                value = slate.wrap_text(child.text, True)
                block_children.append(slate.wrap_paragraph(value))
            elif child.name == "div":
                converter = registry.get_element_converter(child)
                block_children.append(converter(child))
            else:
                block_children.append(deserialize(child))
        block["children"] = block_children
    return block


@registry.element_converter(["pre"], "pre")
def _pre_(element: Element, tag_name: str) -> dict:
    """Deserialize a pre block."""
    # Based on Slate example implementation. Replaces <pre> tags with <code>.
    # Comment: I don't know how good of an idea is this. I'd rather have two
    # separate formats: "preserve whitespace" and "code". This feels like a hack
    children = markup.all_children(element)
    if children and children[0].name == "code":
        converter = registry.get_element_converter(children[0])
        return converter(children[0])

    return _handle_block_(element, tag_name)


@registry.element_converter(["a"], "link")
def _link_(element: Element, tag_name: str) -> dict:
    """Deserializer."""
    children = deserialize_children(element)
    if not children:
        children = [""]
    block = {
        "type": tag_name,
        "data": {
            "url": element.get("href"),
            "title": element.get("title"),
            "target": element.get("target"),
        },
        "children": children,
    }
    return block


@registry.element_converter(["span"])
def _span_(element: Element, tag_name: str) -> dict:
    """Deserialize a span element."""
    styles = markup.styles(element)
    children = markup.all_children(element)
    if len(children) > 1:
        return {"children": deserialize_children(element)}
    else:
        text = element.text
        if styles.get("font-weight", "") == "bold":
            # Handle TinyMCE' bold formatting
            return {"type": "strong", "children": slate.wrap_text(text, True)}
        elif styles.get("font-style", "") == "italic":
            # Handle TinyMCE' italic formatting
            return {"type": "em", "children": slate.wrap_text(text, True)}
        elif styles.get("vertical-align") == "sub":
            # Handle Google Docs' <sub> formatting
            return {"type": "sub", "children": slate.wrap_text(text, True)}
        elif styles.get("vertical-align") == "sup":
            # Handle Google Docs' <sup> formatting
            return {"type": "sup", "children": slate.wrap_text(text, True)}
        elif children:
            return _handle_only_child(children[0], styles)
        elif text:
            return slate.wrap_text(text)


_BLOCK_ELEMENTS_ = [
    "blockquote",
    "p",
    "sub",
    "sup",
    "u",
    "ol",
    "li",
    "dt",
    "dd",
]


@registry.element_converter(_BLOCK_ELEMENTS_)
def _block_(element: Element, tag_name: str) -> dict:
    return _handle_block_(element, tag_name)


def _handle_list_(element: Element, tag_name: str) -> dict:
    block = _handle_block_(element, tag_name)
    children = []
    # Remove not valid child
    for child in block.get("children", []):
        if not (isinstance(child, dict) and child.get("type", "") == "li"):
            continue
        children.append(child)
    block["children"] = children
    return block


@registry.element_converter(["ul"], "ul")
def _ul_(element: Element, tag_name: str) -> dict:
    return _handle_list_(element, tag_name)


@registry.element_converter(["ol"], "ol")
def _ol_(element: Element, tag_name: str) -> dict:
    return _handle_list_(element, tag_name)


@registry.element_converter(["dl"], "dl")
def _dl_(element: Element, tag_name: str) -> dict:
    block = _handle_block_(element, tag_name)
    children = []
    # Remove empty text nodes
    for child in block.get("children", []):
        if slate.is_simple_text(child) and not child["text"].strip():
            continue
        children.append(child)
    block["children"] = children
    return block


@registry.element_converter(["del", "s"], "s")
def _s_(element: Element, tag_name: str) -> dict:
    return _handle_block_(element, tag_name)


@registry.element_converter(["em", "i"], "em")
def _em_(element: Element, tag_name: str) -> dict:
    return _handle_block_(element, tag_name)


def deserialize_children(element: Element) -> list[dict]:
    children = markup.all_children(element)
    block_children = [deserialize(child) for child in children]
    return slate.group_text_blocks(block_children)


def _deserialize(element: Element) -> dict | list | None:
    if markup.is_inline(element) and not element.text.strip():
        response = slate.wrap_text("")
    elif converter := registry.get_block_converter(element):
        # Hack: We 'believe' only slate would return a list of blocks
        blocks = converter(element)
        response = blocks[0] if blocks else None
    elif element_converter := registry.get_element_converter(element):
        response = element_converter(element)
    else:
        response = deserialize_children(element)
    # Clean up response
    if isinstance(response, dict) and slate._just_children(response):
        children = response["children"]
        response = slate.flatten_children(children)

    if not response:
        logger.debug(f"Dropping element {element}")
    return response


def deserialize(element: Element) -> dict | None:
    """Return the JSON-like representation of an element."""
    tag_name = element.name
    text = element.text
    if isinstance(element, Comment):
        logger.debug(f"Dropping element {element}")
        return None
    elif isinstance(element, NavigableString):
        # instead of === '\n' we use isWhitespace for when deserializing tables
        # from Calc and other similar cases
        if not text.strip():
            text = " "
        text = text.replace("\n", " ").replace("\t", " ")
        return slate.wrap_text(text)
    elif tag_name == "br":
        return slate.wrap_text("\n")
    return _deserialize(element)

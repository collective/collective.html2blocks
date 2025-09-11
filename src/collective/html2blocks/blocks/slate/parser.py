"""
Slate block parser for HTML-to-Volto conversion.

This module provides functions and registry-based converters to transform HTML elements
into Slate-compatible JSON structures for Volto/Plone CMS. It supports block-level and
inline elements, handling edge cases for lists, tables, code blocks, and more.

Key features:
- Registry-based element converters for extensibility.
- Generator-based deserialization for efficient tree traversal.
- Handles normalization, whitespace, and special formatting
  (e.g., callouts, code, links).

Example usage:
    from bs4 import BeautifulSoup
    from collective.html2blocks.blocks.slate import parser
    soup = BeautifulSoup('<p>Hello <strong>world</strong></p>', 'html.parser')
    slate_block = parser.deserialize(soup.p)
    # slate_block -> {'type': 'p', 'children': [{'text': 'Hello '},
    #                {'type': 'strong', 'children': [{'text': 'world'}]}]}

Implementation notes:
- Converters are registered via @registry.element_converter for extensibility.
- Generator functions yield intermediate results for composability.
- Utility functions handle normalization and edge cases for Slate blocks.
"""

from bs4 import Comment
from bs4.element import NavigableString
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.logger import logger
from collective.html2blocks.utils import blocks as butils
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate
from collective.html2blocks.utils.generator import item_generator


def extract_blocks(
    raw_children: list[t.SlateBlockItem | t.VoltoBlock],
) -> t.SlateItemsGenerator:
    """
    Extracts Volto blocks from a list of Slate children, yielding Volto blocks and
    collecting non-block children for further processing.

    Args:
        raw_children: List of SlateBlockItem or VoltoBlock dicts.

    Yields:
        VoltoBlock dicts found in the input.

    Returns:
        List of non-block children for further processing.

    Example:
        >>> list(extract_blocks([{'@type': 'image'}, {'type': 'p', 'children': []}]))
        [{'@type': 'image'}]
    """
    raw_children = raw_children if raw_children else []
    children = []
    for child in raw_children:
        if isinstance(child, dict) and butils.is_volto_block(child):
            yield child
        else:
            children.append(child)
    return children


def _instropect_children(child: t.SlateBlockItem) -> t.SlateItemGenerator:
    """
    Recursively introspects and normalizes the children of a Slate block item.

    Args:
        child: SlateBlockItem dict with possible 'children' key.

    Yields:
        Normalized child block items.

    Returns:
        The updated child dict with normalized children.

    """
    children = []
    if child and "children" in child:
        gen = extract_blocks(child["children"])
        children = yield from item_generator(gen)
        child["children"] = children or []
    return child


def finalize_slate(block: t.VoltoBlock) -> t.SlateItemGenerator:
    """
    Finalizes a Slate block by normalizing its children and cleaning up plaintext.

    Args:
        block: VoltoBlock dict with 'value' and 'plaintext' keys.

    Yields:
        Normalized Slate block items.

    Returns:
        The updated block dict with normalized children and cleaned plaintext.
    """
    value = []
    plaintext = block.get("plaintext", "")
    block["plaintext"] = plaintext.strip()
    for raw_item in block.get("value", []):
        if not raw_item:
            continue
        gen = _instropect_children(raw_item)
        item = yield from item_generator(gen)
        if item:
            value.append(item)
    block["value"] = value
    return block


def _handle_only_child(
    child: t.Tag, styles: dict | None = None
) -> t.SlateItemGenerator:
    """
    Handles a single child element, applying block or element converters as needed.

    Args:
        child: BeautifulSoup Tag to process.
        styles: Optional dict of CSS styles.

    Yields:
        Slate block items or wrapped text/paragraphs.

    Returns:
        Normalized Slate block item or text.
    """
    text = child.text
    styles = styles if styles else {}
    if block_converter := registry.get_block_converter(child):
        yield from block_converter(child)
    elif not text.strip():
        gen = deserialize_children(child)
        block_children = yield from item_generator(gen)
        if block_children and isinstance(block_children, list):
            return slate.wrap_paragraph(block_children)
        else:
            return slate.wrap_text(" ")
    elif element_converter := registry.get_element_converter(child):
        gen = element_converter(child)
        result = yield from item_generator(gen)
        return result
    return slate.wrap_text(text)


def _handle_block_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """
    Handles block-level elements, normalizing children and applying special formatting.

    Args:
        element: BeautifulSoup Tag representing the block element.
        tag_name: Name of the block tag (e.g., 'p', 'blockquote').

    Yields:
        Normalized Slate block items.

    Returns:
        Slate block item dict with normalized children.
    """
    gen = deserialize_children(element)
    block_children: list[t.SlateBlockItem] = yield from item_generator(gen)
    if not block_children:
        return None
    total_children = len(block_children)
    first_child = block_children[0] if total_children else None
    if total_children == 1 and first_child:
        child_type = first_child.get("type")
        if tag_name in ("p", "blockquote") and child_type == "p":
            block_children = first_child.get("children", [])
            first_child = block_children[0] if total_children else None
    response: t.SlateBlockItem = {"type": tag_name}
    if tag_name in ("td", "th") and block_children and isinstance(first_child, str):
        block_children = [slate.wrap_paragraph([slate.wrap_text(first_child)])]
    if slate.has_internal_block(block_children):
        internal_children = slate.normalize_block_nodes(block_children, tag_name)
        if (
            len(internal_children) == 1
            and internal_children[0].get("type") == response["type"]
        ):
            block_children = internal_children[0]["children"]
        elif len(internal_children) > 1:
            block_children = internal_children
    if tag_name == "p" and "callout" in markup.css_classes(element):
        response["type"] = "callout"
    response["children"] = block_children
    return slate.process_children(response)


@registry.element_converter(["br"])
def _br_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Convert br tag to newline text."""
    result = slate.wrap_text("\n")
    yield
    return result


@registry.element_converter(["hr"], "p")
def _hr_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Convert hr tag to empty paragraph."""
    children = [slate.wrap_text("")]
    result = {"type": tag_name, "children": children}
    yield
    return result


@registry.element_converter(["body"])
def _body_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserialize body tag."""
    gen = deserialize_children(element)
    children = yield from item_generator(gen)
    return {"children": children}


@registry.element_converter(["h1", "h2", "h3", "h4", "h5", "h6"])
def _header_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_block_(element, tag_name)
    block = yield from item_generator(gen)
    if not block:
        return None
    valid_subblocks = []
    for child in block.get("children", []):
        if slate.invalid_subblock(child):
            yield child
        else:
            valid_subblocks.append(child)
    block["children"] = valid_subblocks
    return block


@registry.element_converter(["b", "strong"], "strong")
def _strong_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserialize b and strong tags."""
    gen = deserialize_children(element)
    children = yield from item_generator(gen)
    return {"type": tag_name, "children": children}


@registry.element_converter(["code"], "code")
def _code_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserialize Code Block."""
    # CHECK
    text = element.text
    yield
    return {"type": tag_name, "text": text}


@registry.element_converter(["div"], "div")
def _div_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserialize a div block."""
    styles = markup.styles(element)
    children = markup.all_children(element)
    block = {}
    if len(children) == 1:
        child = children[0]
        block = yield from item_generator(_handle_only_child(child, styles))
    else:
        block_children = []
        for child in children:
            if isinstance(child, NavigableString):
                value = [slate.wrap_text(child.text)]
                block_children.append(slate.wrap_paragraph(value))
            elif child.name == "div":
                gen = _div_(child)
                child_block = yield from item_generator(gen)
                block_children.append(child_block)
            else:
                gen = deserialize(child)
                child_block = yield from item_generator(gen)
                block_children.append(child_block)
        block["children"] = block_children
    return block


@registry.element_converter(["pre"], "pre")
def _pre_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserialize a pre block."""
    # Based on Slate example implementation. Replaces <pre> tags with <code>.
    # Comment: I don't know how good of an idea is this. I'd rather have two
    # separate formats: "preserve whitespace" and "code". This feels like a hack
    children = markup.all_children(element)
    if children and children[0].name == "code":
        child = children[0]
        gen = _code_(child)
        item = yield from item_generator(gen)
        return item
    gen = _handle_block_(element, tag_name)
    item = yield from item_generator(gen)
    return item


@registry.element_converter(["a"], "link")
def _link_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserializer."""
    gen = deserialize_children(element)
    children = yield from item_generator(gen)
    children = slate.remove_empty_text(children)
    if not children:
        return slate.wrap_text("")

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
def _span_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    """Deserialize a span element."""
    styles = markup.styles(element)
    children = markup.all_children(element)
    if len(children) > 1:
        gen = deserialize_children(element)
        children = yield from item_generator(gen)
        return {"children": children}
    text = element.text
    if styles.get("font-weight", "") == "bold":
        # Handle TinyMCE' bold formatting
        return {"type": "strong", "children": [slate.wrap_text(text)]}
    elif styles.get("font-style", "") == "italic":
        # Handle TinyMCE' italic formatting
        return {"type": "em", "children": [slate.wrap_text(text)]}
    elif styles.get("vertical-align") == "sub":
        # Handle Google Docs' <sub> formatting
        return {"type": "sub", "children": [slate.wrap_text(text)]}
    elif styles.get("vertical-align") == "sup":
        # Handle Google Docs' <sup> formatting
        return {"type": "sup", "children": [slate.wrap_text(text)]}
    elif children:
        gen = _handle_only_child(children[0], styles)
        item = yield from item_generator(gen)
        if text:
            return item
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
def _block_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_block_(element, tag_name)
    item = yield from item_generator(gen)
    return item


def _handle_list_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_block_(element, tag_name)
    item = yield from item_generator(gen)
    if not item:
        return
    children = []
    allowed_children = ["li", tag_name]
    # Remove not valid child
    for child in item.get("children", []):
        if not (isinstance(child, dict) and child.get("type", "") in allowed_children):
            continue
        children.append(child)
    if not children:
        return None
    item["children"] = children
    return item


@registry.element_converter(["ul"], "ul")
def _ul_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_list_(element, tag_name)
    item = yield from item_generator(gen)
    return item


@registry.element_converter(["ol"], "ol")
def _ol_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_list_(element, tag_name)
    item = yield from item_generator(gen)
    return item


@registry.element_converter(["dl"], "dl")
def _dl_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_block_(element, tag_name)
    item = yield from item_generator(gen)
    if not item:
        return
    children = []
    # Remove empty text nodes
    for child in item.get("children", []):
        if slate.is_simple_text(child) and not child.get("text", "").strip():
            continue
        children.append(child)
    if not children:
        return None
    item["children"] = children
    return item


@registry.element_converter(["del", "s"], "s")
def _s_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_block_(element, tag_name)
    item = yield from item_generator(gen)
    return item


@registry.element_converter(["em", "i"], "em")
def _em_(element: t.Tag, tag_name: str) -> t.SlateItemGenerator:
    gen = _handle_block_(element, tag_name)
    item = yield from item_generator(gen)
    return item


def deserialize_children(element: t.Tag) -> t.SlateItemsGenerator:
    """
    Deserializes all children of an element into Slate-compatible blocks.

    Args:
        element: BeautifulSoup Tag whose children will be deserialized.

    Yields:
        Slate block items for each child.

    Returns:
        Grouped text blocks or an empty list.
    """
    children = markup.all_children(element)
    block_children = []
    for child in children:
        info = yield from item_generator(deserialize(child))
        block_children.append(info)
    return slate.group_text_blocks(block_children) or []


def _deserialize(element: t.Tag) -> t.SlateItemsGenerator:
    """
    Internal deserialization logic for an element, applying block/element converters or
    recursively deserializing children.

    Args:
        element: BeautifulSoup Tag to deserialize.

    Yields:
        Slate block items or text.

    Returns:
        Normalized Slate block item(s) or text.
    """
    if markup.is_inline(element) and not element.text.strip():
        response = slate.wrap_text("")
    elif converter := registry.get_block_converter(element):
        # Hack: We 'believe' only slate would return a list of blocks
        gen = converter(element)
        yield from converter(element)
        return []
    elif element_converter := registry.get_element_converter(element):
        gen = element_converter(element)
        response = yield from item_generator(gen)
    else:
        gen = deserialize_children(element)
        response = yield from item_generator(gen)
    # Clean up response
    if response and isinstance(response, dict) and slate._just_children(response):
        children = response["children"]
        response = slate.flatten_children(children)

    if not response:
        logger.debug(f"Dropping element {element}")
    return response


def deserialize(element: t.Tag) -> t.SlateItemGenerator:
    """
    Return the JSON-like Slate representation of an HTML element.

    This is the main entry point for converting a BeautifulSoup Tag into a Slate block
    or text node. Handles comments, whitespace, block/element converters, and recursive
    deserialization.

    Args:
        element: BeautifulSoup Tag to convert.

    Yields:
        Slate block items or text nodes.

    Returns:
        Slate block item or None if dropped.

    Example:
        >>> from bs4 import BeautifulSoup
        >>> soup = BeautifulSoup('<p>Hello <strong>world</strong></p>', 'html.parser')
        >>> deserialize(soup.p)
        {'type': 'p', 'children': [{'text': 'Hello '},
        {'type': 'strong', 'children': [{'text': 'world'}]}]}
    """
    if isinstance(element, Comment):
        logger.debug(f"Dropping element {element}")
        return None
    elif isinstance(element, NavigableString):
        # instead of === '\n' we use isWhitespace for when deserializing tables
        # from Calc and other similar cases
        text = element.text
        if not text.strip():
            text = " "
        text = text.replace("\n", " ").replace("\t", " ")
        return slate.wrap_text(text)
    elif element.name == "br":
        return slate.wrap_text("\n")
    gen = _deserialize(element)
    slate_item = yield from item_generator(gen)
    return slate_item if slate_item else None

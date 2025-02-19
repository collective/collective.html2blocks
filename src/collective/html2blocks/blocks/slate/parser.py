from bs4 import Comment
from bs4.element import NavigableString
from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate


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
        if first_child.get("@type"):
            # Check if we already have a block information
            return first_child
        child_type = first_child.get("type")
        if tag_name in ("p", "blockquote") and child_type == "p":
            block_children = first_child["children"]
    if len(block_children) == 1 and first_child.get("@type"):
        return first_child
    response = {
        "type": tag_name,
    }

    if tag_name in ("td", "th") and block_children and isinstance(first_child, str):
        block_children = [{"type": "p", "chidren": slate.wrap_text(first_child, True)}]
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
    response = block
    valid_subblocks = []
    invalid_subblocks = []
    for child in block["children"]:
        type_ = child.get("type", child.get("@type", ""))
        if type_ in ("image", "video", "slateTable"):
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
        block = (
            {"type": "p", "children": [block]} if slate.is_simple_text(block) else block
        )
    else:
        block_children = []
        for child in children:
            if isinstance(child, NavigableString):
                value = child.text
                block_children.append({
                    "type": "p",
                    "children": slate.wrap_text(value, True),
                })
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


@registry.element_converter([
    "blockquote",
    "p",
    "sub",
    "sup",
    "u",
    "ol",
    "ul",
    "li",
    "dl",
    "dt",
    "dd",
])
def _block_(element: Element, tag_name: str) -> dict:
    return _handle_block_(element, tag_name)


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


def deserialize(element: Element) -> dict | None:
    """Return the JSON-like representation of an element."""
    tag_name = element.name
    text = element.text
    if isinstance(element, Comment):
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
    response = None
    if markup.is_inline(element) and not text.strip():
        response = slate.wrap_text("")
    elif converter := registry.get_block_converter(element):
        # Hack: We 'believe' only slate would return a list of blocks
        response = converter(element)[0]
    elif element_converter := registry.get_element_converter(element):
        response = element_converter(element)
    else:
        response = deserialize_children(element)
    if isinstance(response, dict) and slate._just_children(response):
        response = response["children"]
    return response

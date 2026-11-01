"""
Slate to Plate utilities for ``collective.html2blocks``.

Plone Aurora keeps a whole page in one Plate value, stored in the ``__somersault__``
block. This module ports the migrations Aurora applies at runtime, so the content can
be converted ahead of time, and adds what the Slate converter emits and those
migrations do not cover: more marks, nested lists, ``pre`` elements and tables.

Plate keeps the data model of Slate, so a Slate value only needs structural changes,
and the conversion to Plate reuses the Slate converter unchanged.

Example:
    .. code-block:: python

        from collective.html2blocks.utils import plate
        slate_blocks = [{"@type": "title"}, {"@type": "slate", "value": [...]}]
        value = plate.value_from_blocks(slate_blocks, title="Welcome")
        block = plate.somersault_block(value)
"""

from collections.abc import Mapping
from collective.html2blocks import _types as t
from copy import deepcopy
from typing import Any


SOMERSAULT_KEY = "__somersault__"
PLONE_BLOCK_TYPE = "ploneBlock"
TITLE_BLOCK_TYPE = "title"
TABLE_BLOCK_TYPE = "slateTable"
CODE_BLOCK_TYPE = "codeBlock"
DEFAULT_BLOCK_WIDTH = "default"
BLOCK_WIDTHS = ("narrow", DEFAULT_BLOCK_WIDTH, "layout", "full")

# Slate element types that are text marks in Plate.
MARKS = {
    "strong": "bold",
    "em": "italic",
    "del": "strikethrough",
    "s": "strikethrough",
    "u": "underline",
    "sub": "subscript",
    "sup": "superscript",
    "code": "code",
}
LIST_STYLES = {"ul": "disc", "ol": "decimal"}
INLINE_TYPES = frozenset({"a", "link", "mention", "inline_equation", "date"})


def _is_text(node: t.PlateNode) -> bool:
    """Check if a node is a text leaf."""
    return isinstance(node.get("text"), str)


def _is_inline(node: t.PlateNode) -> bool:
    """Check if a node is a text leaf or an inline element."""
    return _is_text(node) or node.get("type") in INLINE_TYPES


def _text_content(node: t.PlateNode) -> str:
    """Return the text of a node and its descendants."""
    if _is_text(node):
        return node["text"]
    return "".join(_text_content(child) for child in node.get("children", []))


def _wrap_inline(children: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Wrap runs of inline children in paragraphs, keeping the block children.

    :param children: The children of a container, such as a blockquote.
    :returns: Block children only, with at least one paragraph.
    """
    blocks: list[t.PlateNode] = []
    inline_run: list[t.PlateNode] = []
    for child in children:
        if _is_inline(child):
            inline_run.append(child)
            continue
        if inline_run:
            blocks.append({"type": "p", "children": inline_run})
            inline_run = []
        blocks.append(child)
    if inline_run:
        blocks.append({"type": "p", "children": inline_run})
    return blocks or [{"type": "p", "children": [{"text": ""}]}]


def _mark_node(node: t.PlateNode, marks: dict[str, bool]) -> list[t.PlateNode]:
    """Apply the marks of a node to its text, and unwrap it if it is a mark."""
    mark = MARKS.get(node.get("type", ""))
    if mark:
        marks = {**marks, mark: True}
    if _is_text(node):
        if mark:
            del node["type"]
        for name, value in marks.items():
            node.setdefault(name, value)
        return [node]
    if not isinstance(node.get("children"), list):
        return [node]
    children = [item for child in node["children"] for item in _mark_node(child, marks)]
    if mark:
        return children
    node["children"] = children or [{"text": ""}]
    return [node]


def migrate_marks(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Turn Slate mark elements into marks on the text nodes.

    :param value: The Slate value, changed in place.
    :returns: The migrated value.

    Example:
        .. code-block:: pycon

            >>> migrate_marks([{"type": "strong", "children": [{"text": "bold"}]}])
            [{'text': 'bold', 'bold': True}]
    """
    return [item for node in value for item in _mark_node(node, {})]


def _migrate_link(node: t.PlateNode) -> None:
    """Move the link data of a node to the attributes Plate reads."""
    data = node.get("data")
    if isinstance(data, Mapping) and isinstance(data.get("url"), str):
        node["type"] = "a"
        node["url"] = data["url"]
        if target := data.get("target"):
            node["target"] = target
        del node["data"]
    elif node.get("type") == "link":
        node["type"] = "a"
        if isinstance(data, Mapping) and not any(data.values()):
            del node["data"]
    for child in node.get("children", []):
        _migrate_link(child)


def migrate_links(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Turn Slate links into Plate links.

    The ``url`` and ``target`` of ``data`` become attributes of the node, and the
    type becomes ``a``.

    :param value: The Slate value, changed in place.
    :returns: The migrated value.

    Example:
        .. code-block:: pycon

            >>> migrate_links([{"type": "link", "data": {"url": "/a"}, "children": []}])
            [{'type': 'a', 'children': [], 'url': '/a'}]
    """
    for node in value:
        _migrate_link(node)
    return value


def _list_item_nodes(item: t.PlateNode, depth: int) -> list[t.PlateNode]:
    """
    Return the nodes of a list item, before the list markers are added.

    :param item: The ``li`` node.
    :param depth: The depth of the list the item belongs to.
    :returns: Block nodes. The nested lists are already flattened.
    """
    nodes: list[t.PlateNode] = []
    inline_run: list[t.PlateNode] = []

    def _flush_inline() -> None:
        if inline_run:
            nodes.append({"type": "p", "children": list(inline_run)})
            inline_run.clear()

    for child in item.get("children") or [{"text": ""}]:
        if _is_inline(child):
            inline_run.append(child)
        elif child.get("type") in LIST_STYLES:
            _flush_inline()
            nodes.extend(_flatten_list(child, depth + 1))
        else:
            _flush_inline()
            nodes.extend(_migrate_list_node(child))
    _flush_inline()
    return nodes


def _flatten_list(node: t.PlateNode, depth: int = 1) -> list[t.PlateNode]:
    """
    Flatten a list into paragraphs with list markers.

    The ``indent`` of a node is the depth of its list. In a list item with several
    blocks, the first one carries the marker, and the others continue the item.

    :param node: The ``ul`` or ``ol`` node.
    :param depth: The depth of the list.
    :returns: The flattened nodes.
    """
    style = LIST_STYLES[node["type"]]
    nodes: list[t.PlateNode] = []
    position = 0
    for item in node.get("children", []):
        if not isinstance(item.get("children"), list):
            continue
        if item.get("type") in LIST_STYLES:
            nodes.extend(_flatten_list(item, depth + 1))
            continue
        position += 1
        first = True
        for child in _list_item_nodes(item, depth):
            if "indent" in child:
                nodes.append(child)
                continue
            child["indent"] = depth
            if first:
                child["listStyleType"] = style
                if position > 1:
                    child["listStart"] = position
                elif style == "decimal":
                    child["listRestartPolite"] = 1
                first = False
            nodes.append(child)
    return nodes


def _migrate_list_node(node: t.PlateNode) -> list[t.PlateNode]:
    """Flatten a node if it is a list, or the lists among its children."""
    if node.get("type") in LIST_STYLES:
        return _flatten_list(node)
    if isinstance(node.get("children"), list):
        node["children"] = migrate_lists(node["children"])
    return [node]


def migrate_lists(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Turn Slate lists into paragraphs with list markers.

    :param value: The Slate value, changed in place.
    :returns: The migrated value.

    Example:
        .. code-block:: pycon

            >>> item = {"type": "li", "children": [{"text": "one"}]}
            >>> migrate_lists([{"type": "ul", "children": [item]}])
            [{'type': 'p', 'children': [{'text': 'one'}], 'indent': 1, 'listStyleType': 'disc'}]
    """  # noqa: E501
    return [item for node in value for item in _migrate_list_node(node)]


def migrate_blockquotes(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Turn flat Slate blockquotes into Plate containers of block nodes.

    :param value: The Slate value, changed in place.
    :returns: The migrated value.

    Example:
        .. code-block:: pycon

            >>> migrate_blockquotes([{"type": "blockquote", "children": [{"text": "q"}]}])
            [{'type': 'blockquote', 'children': [{'type': 'p', 'children': [{'text': 'q'}]}]}]
    """  # noqa: E501
    for node in value:
        children = node.get("children")
        if not isinstance(children, list):
            continue
        if node.get("type") == "blockquote" and any(map(_is_inline, children)):
            node["children"] = _wrap_inline(children)
        migrate_blockquotes(node["children"])
    return value


def _code_block(code: str, lang: str = "") -> t.PlateNode:
    """
    Return a Plate code block, with one child per line.

    :param code: The code.
    :param lang: The language. Without one, Aurora shows plain text.
    :returns: The ``code_block`` node.
    """
    children = [
        {"type": "code_line", "children": [{"text": line}]} for line in code.split("\n")
    ]
    node: t.PlateNode = {"type": "code_block", "children": children}
    if lang:
        node["lang"] = lang
    return node


def migrate_code_blocks(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Turn ``pre`` elements into Plate code blocks, with one child per line.

    :param value: The Slate value, changed in place.
    :returns: The migrated value.

    Example:
        .. code-block:: pycon

            >>> migrate_code_blocks([{"type": "pre", "children": [{"text": "ls"}]}])
            [{'type': 'code_block', 'children': [{'type': 'code_line', 'children': [{'text': 'ls'}]}]}]
    """  # noqa: E501
    for node in value:
        if node.get("type") == "pre":
            node.update(_code_block(_text_content(node)))
        elif isinstance(node.get("children"), list):
            migrate_code_blocks(node["children"])
    return value


def migrate_block_widths(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """
    Set the width of the top-level native nodes that have no valid one.

    :param value: The Plate value, changed in place.
    :returns: The migrated value.
    """
    for node in value:
        if not isinstance(node.get("type"), str) or node["type"] == PLONE_BLOCK_TYPE:
            continue
        if node.get("blockWidth") not in BLOCK_WIDTHS:
            node["blockWidth"] = DEFAULT_BLOCK_WIDTH
    return value


def _migrate_nodes(value: list[t.PlateNode]) -> list[t.PlateNode]:
    """Apply the migrations that also hold for nodes nested in a container."""
    value = migrate_marks(value)
    value = migrate_links(value)
    value = migrate_lists(value)
    value = migrate_blockquotes(value)
    return migrate_code_blocks(value)


def migrate_value(value: list[t.SlateBlockItem]) -> list[t.PlateNode]:
    """
    Convert a Slate value to a Plate value.

    Running it on a value it already converted changes nothing.

    :param value: The Slate value, which is left unchanged.
    :returns: The Plate value.

    Example:
        .. code-block:: pycon

            >>> value = [{"type": "p", "children": [{"text": "Hello"}]}]
            >>> migrate_value(value)
            [{'type': 'p', 'children': [{'text': 'Hello'}], 'blockWidth': 'default'}]
    """
    return migrate_block_widths(_migrate_nodes(deepcopy(value)))


def _table_cell(cell: Mapping[str, Any]) -> t.PlateNode:
    """Convert a cell of a Slate table to a Plate cell."""
    raw_value = cell.get("value") or []
    children = [{"text": item} if isinstance(item, str) else item for item in raw_value]
    return {
        "type": "th" if cell.get("type") == "header" else "td",
        "children": _wrap_inline(_migrate_nodes(deepcopy(children))),
    }


def _table_node(block: t.VoltoBlock) -> t.PlateNode:
    """
    Convert a ``slateTable`` block to a native Plate table.

    :param block: The ``slateTable`` block.
    :returns: The Plate table. The first row is left out when the block hides it.
    """
    table = block.get("table", {})
    rows = table.get("rows", [])
    if table.get("hideHeaders"):
        rows = rows[1:]
    return {
        "type": "table",
        "children": [
            {
                "type": "tr",
                "children": [_table_cell(cell) for cell in row.get("cells", [])],
            }
            for row in rows
        ],
    }


def nodes_from_block(block: t.VoltoBlock, title: str = "") -> list[t.PlateNode]:
    """
    Convert a Volto block to the nodes that replace it in a Plate value.

    A ``title`` block becomes a ``title`` node, and a block with a ``value`` list
    contributes that value. A ``slateTable`` and a ``codeBlock`` become native Plate
    nodes, because Aurora has no such blocks. Every other block is wrapped in a
    ``ploneBlock`` node.
    Aurora drops a block that is not registered in the site, but this conversion
    can't see that registry, so it keeps the data of every block.

    :param block: The Volto block, which is left unchanged.
    :param title: The title of the content, for a ``title`` block.
    :returns: The nodes, still to be migrated with :func:`migrate_value`.

    Example:
        .. code-block:: pycon

            >>> nodes_from_block({"@type": "title"}, title="Welcome")
            [{'type': 'title', 'children': [{'text': 'Welcome'}]}]
    """
    block_type = block.get("@type")
    if block_type == TITLE_BLOCK_TYPE:
        return [{"type": TITLE_BLOCK_TYPE, "children": [{"text": title}]}]
    if isinstance(value := block.get("value"), list):
        return value
    if block_type == TABLE_BLOCK_TYPE:
        return [_table_node(block)]
    if block_type == CODE_BLOCK_TYPE:
        language = block.get("language", "")
        return [
            _code_block(block.get("code", ""), "" if language == "text" else language)
        ]
    width = block.get("blockWidth") or DEFAULT_BLOCK_WIDTH
    return [
        {
            **deepcopy(block),
            "blockWidth": width,
            "type": PLONE_BLOCK_TYPE,
            "children": [{"text": ""}],
        }
    ]


def value_from_blocks(blocks: list[t.VoltoBlock], title: str = "") -> list[t.PlateNode]:
    """
    Convert a list of Volto blocks to a Plate value.

    :param blocks: The Volto blocks, in order.
    :param title: The title of the content, for a ``title`` block.
    :returns: The Plate value.
    """
    nodes = [node for block in blocks for node in nodes_from_block(block, title)]
    return migrate_value(nodes)


def somersault_block(value: list[t.PlateNode]) -> t.VoltoBlock:
    """
    Wrap a Plate value in the block that holds a whole page in Aurora.

    :param value: The Plate value.
    :returns: The ``__somersault__`` block.
    """
    return {"@type": SOMERSAULT_KEY, "value": value}


def info_from_blocks(blocks: list[t.VoltoBlock], title: str = "") -> t.VoltoBlocksInfo:
    """
    Construct the blocks info of a page from a list of Volto blocks.

    :param blocks: The Volto blocks, in order.
    :param title: The title of the content, for a ``title`` block.
    :returns: Dictionary with the ``__somersault__`` block as its only block.
    """
    value = value_from_blocks(blocks, title)
    return {
        "blocks": {SOMERSAULT_KEY: somersault_block(value)},
        "blocks_layout": {"items": []},
    }


def migrate_content(content: Mapping[str, Any], title: str | None = None) -> dict:
    """
    Add the ``__somersault__`` block to a content item with Slate blocks.

    Like the migration of Aurora, this is additive and idempotent: the existing
    blocks stay, and a content item that already has the block is returned as it
    is, as is one without ``blocks`` or a ``blocks_layout`` list.

    :param content: The content item, which is left unchanged.
    :param title: The title for a ``title`` block. Defaults to the ``title`` key
        of the content item.
    :returns: A copy of the content item.

    Example:
        .. code-block:: pycon

            >>> content = {
            ...     "title": "Welcome",
            ...     "blocks": {"a": {"@type": "title"}},
            ...     "blocks_layout": {"items": ["a"]},
            ... }
            >>> migrate_content(content)["blocks"]["__somersault__"]["value"]
            [{'type': 'title', 'children': [{'text': 'Welcome'}], 'blockWidth': 'default'}]
    """  # noqa: E501
    migrated = dict(content)
    blocks = content.get("blocks")
    items = (content.get("blocks_layout") or {}).get("items")
    if not blocks or not isinstance(items, list) or SOMERSAULT_KEY in blocks:
        return migrated
    if title is None:
        raw_title = content.get("title")
        title = raw_title if isinstance(raw_title, str) else ""
    ordered = [blocks[item] for item in items if item in blocks]
    value = value_from_blocks(ordered, title)
    migrated["blocks"] = {**blocks, SOMERSAULT_KEY: somersault_block(value)}
    return migrated

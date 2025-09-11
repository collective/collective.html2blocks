"""
Table block converter for collective.html2blocks.

This module provides the block converter for <table> elements, transforming them
into Volto table blocks. It handles header detection, row and cell extraction,
cell type assignment, and supports nested blocks within table cells.

Implementation details:
- Detects header rows and can hide headers if the table lacks explicit <th> cells.
- Extracts and normalizes cell values, supporting both text and nested blocks.
- Uses helper functions for cell value processing and row extraction.
- Yields the main table block and any additional blocks found within cells.

Example usage::

    from collective.html2blocks.blocks.table import table_block
    blocks = list(table_block(element))
"""

from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.blocks.slate import parser
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate
from collective.html2blocks.utils.generator import item_generator


INVALID_TABLE_CELL_TAGS = (
    "iframe",
    "img",
    "table",
    "video",
)

VALID_TABLE_CELL_TAGS = (
    "td",
    "th",
    "tr",
)


def _process_cell_value(
    raw_cell_value: list | dict,
) -> Generator[t.VoltoBlock | None, None, list[t.SlateBlockItem]]:
    if len(raw_cell_value) == 0:
        raw_cell_value = [""]
    elif {slate.is_simple_text(v) for v in raw_cell_value} == {True}:
        raw_cell_value = ["".join([v["text"] for v in raw_cell_value])]
    cell_value = []
    for value in raw_cell_value:
        if isinstance(value, str):
            value = {"text": value}
        elif slate.invalid_subblock(value):
            # Add the subblock to the list of blocks
            yield value
            # But we add an empty value into the cell
            value = {"text": ""}
        cell_value.append(value)
    return cell_value


@registry.block_converter("table")
def table_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """
    Convert a <table> element to a Volto table block.

    This converter extracts rows, headers, and cell values from the table element,
    normalizes cell content, and yields a Volto table block. Additional blocks
    found within table cells are also yielded.

    Args:
        element (Tag): The <table> element to convert.

    Yields:
        VoltoBlock: The converted table block and any nested blocks.

    Example::

        blocks = list(table_block(element))
        # [{'@type': 'slateTable', 'table': {...}}, ...]
    """
    additional_blocks: list[t.VoltoBlock] = []
    block: t.VoltoBlock = {"@type": "slateTable"}
    rows = []
    css_classes: list[str] = element.get("class", [])
    hide_headers = False
    is_first_row = True
    table_rows, possible_blocks = markup.extract_rows_and_possible_blocks(
        element, list(INVALID_TABLE_CELL_TAGS)
    )
    for row, is_header in table_rows:
        row_cells = [
            tag
            for tag in markup.all_children(row, allow_tags=list(VALID_TABLE_CELL_TAGS))
            if isinstance(tag, t.Tag)
        ]
        if not row_cells:
            continue
        first_cell = row_cells[0].name if row_cells else None
        if first_cell == "th" or is_header:
            is_first_row = False
        elif is_first_row and first_cell != "th":
            is_first_row = False
            # if first cell is not a TH, we assume we have a table without header.
            # so we add an empty header row and hide it via `hideHeaders`.
            # (otherwise the first row would appear as header what might no be expected)
            empty_header_cells: list[t.SlateBlockItem] = [
                slate.table_cell("header", [""]) for _ in row_cells
            ]
            hide_headers = True
            rows.append(slate.table_row(empty_header_cells))
        cells = []
        for cell in row_cells:
            cell_type = markup.table_cell_type(cell, is_header)
            raw_cell_value = yield from item_generator(
                parser.deserialize_children(cell)
            )
            cell_value = yield from item_generator(_process_cell_value(raw_cell_value))
            if cell_value:
                cells.append(slate.table_cell(cell_type, cell_value))

        rows.append(slate.table_row(cells))
    block["table"] = slate.table(
        rows=rows, hide_headers=hide_headers, css_classes=css_classes
    )
    # Main table block
    yield block
    # Blocks we found in the table cells
    yield from additional_blocks
    # Blocks we found during parsing of the table
    for element in possible_blocks:
        block_converter = registry.get_block_converter(element, strict=False)
        if not block_converter:
            continue
        yield from block_converter(element)

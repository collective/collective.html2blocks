from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.blocks.slate import parser
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate


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
) -> tuple[list[dict], list[VoltoBlock]]:
    blocks: list[VoltoBlock] = []
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
            blocks.append(value)
            # But we add an empty value into the cell
            value = {"text": ""}
        cell_value.append(value)
    return cell_value, blocks


@registry.block_converter("table")
def table_block(element: Element) -> list[VoltoBlock]:
    """Return a table block."""
    blocks: list[VoltoBlock] = []
    block = {"@type": "slateTable"}
    rows = []
    css_classes: list[str] = element.get("class", [])
    hide_headers = False
    is_first_row = True
    table_rows, possible_blocks = markup.extract_rows_and_possible_blocks(
        element, INVALID_TABLE_CELL_TAGS
    )
    for row, is_header in table_rows:
        row_cells = markup.all_children(row, allow_tags=VALID_TABLE_CELL_TAGS)
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
            empty_header_cells = [slate.table_cell("header", [""]) for _ in row_cells]
            hide_headers = True
            rows.append(slate.table_row(empty_header_cells))
        cells = []
        for cell in row_cells:
            cell_type = markup.table_cell_type(cell, is_header)
            raw_cell_value = parser.deserialize_children(cell)
            cell_value, additional_blocks = _process_cell_value(raw_cell_value)
            cells.append(slate.table_cell(cell_type, cell_value))
            if additional_blocks:
                blocks.extend(additional_blocks)
        rows.append(slate.table_row(cells))
    block["table"] = slate.table(
        rows=rows, hide_headers=hide_headers, css_classes=css_classes
    )
    blocks.insert(0, block)
    for element in possible_blocks:
        block_converter = registry.get_block_converter(element, strict=False)
        el_blocks = block_converter(element) if block_converter else []
        if el_blocks:
            blocks.extend(el_blocks)
    return blocks

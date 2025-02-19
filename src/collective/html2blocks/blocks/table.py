from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks.blocks.slate import parser
from collective.html2blocks.utils import markup
from collective.html2blocks.utils import slate


@registry.block_converter("table")
def table_block(element: Element) -> list[dict]:
    """Return a table block."""
    block = {"@type": "slateTable"}
    rows = []
    css_classes: list[str] = element.get("class", [])
    hide_headers = False
    is_first_row = True
    table_rows = markup.extract_table_rows(element)
    for child, is_header in table_rows:
        children = markup.all_children(child)
        first_child_name = children[0].name if children else None
        if first_child_name == "th" or is_header:
            is_first_row = False
        elif is_first_row and first_child_name != "th":
            is_first_row = False
            # if first cell is not a TH, we assume we have a table without header.
            # so we add an empty header row and hide it via `hideHeaders`.
            # (otherwise the first row would appear as header what might no be expected)
            empty_header_cells = [slate.table_cell("header", [""]) for _ in children]
            hide_headers = True
            rows.append(slate.table_row(empty_header_cells))
        cells = []
        for cell in children:
            cell_type = markup.table_cell_type(cell, is_header)
            raw_cell_value = parser.deserialize_children(cell)
            if len(raw_cell_value) == 0:
                raw_cell_value = [""]
            elif {slate.is_simple_text(v) for v in raw_cell_value} == {True}:
                raw_cell_value = ["".join([v["text"] for v in raw_cell_value])]
            cell_value = []
            for value in raw_cell_value:
                if isinstance(value, str):
                    value = {"text": value}
                cell_value.append(value)
            cells.append(slate.table_cell(cell_type, cell_value))
        rows.append(slate.table_row(cells))
    block["table"] = slate.table(
        rows=rows, hide_headers=hide_headers, css_classes=css_classes
    )
    return [block]

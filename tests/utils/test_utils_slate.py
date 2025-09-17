from collective.html2blocks.utils import slate
from typing import Any

import pytest


@pytest.mark.parametrize(
    "block_children,expected",
    [
        [
            [{"text": "Hello world!"}, {"text": ""}],
            [{"text": "Hello world!"}],
        ]
    ],
)
def test_group_text_blocks(block_children: list[dict], expected: list[dict]):
    func = slate.group_text_blocks
    assert func(block_children) == expected


def test__get_id():
    func = slate._get_id
    result = func()
    assert isinstance(result, str)
    assert result.isdigit()


@pytest.mark.parametrize(
    "rows,css_classes,hide_headers,key,expected",
    [
        [["", ""], [], True, "hideHeaders", True],
        [["", ""], [], False, "hideHeaders", False],
        [["", ""], [], False, "basic", False],
        [["", ""], [], False, "celled", True],
        [["", ""], [], False, "compact", False],
        [["", ""], [], False, "fixed", True],
        [["", ""], [], False, "inverted", False],
        [["", ""], [], False, "striped", False],
        [["", ""], ["ui", "table", "striped"], False, "striped", True],
    ],
)
def test_table(
    rows: list, css_classes: list[str], hide_headers: bool, key: str, expected: Any
):
    func = slate.table
    result = func(rows, css_classes, hide_headers)
    assert result[key] == expected


def test_table_row():
    func = slate.table_row
    result = func([""])
    assert isinstance(result, dict)
    assert "key" in result
    assert "cells" in result
    assert isinstance(result["cells"], list)


@pytest.mark.parametrize(
    "cell_type,value",
    [
        ["th", ["", ""]],
        ["td", ["", ""]],
    ],
)
def test_table_cell(cell_type: str, value: list):
    func = slate.table_cell
    result = func(cell_type, value)
    assert isinstance(result, dict)
    assert "key" in result
    assert result["type"] == cell_type
    assert "value" in result
    assert isinstance(result["value"], list)


@pytest.mark.parametrize(
    "raw_value,expected",
    [
        [
            [{"text": "Hello world!"}, {"text": ""}],
            [{"children": [{"text": "Hello world!"}, {"text": ""}], "type": "p"}],
        ],
        [
            [
                {"children": [{"text": "Hello world!"}], "type": "p"},
                {"text": "Olá"},
                {"text": "Mundo"},
            ],
            [
                {"children": [{"text": "Hello world!"}], "type": "p"},
                {"children": [{"text": "Olá"}, {"text": "Mundo"}], "type": "p"},
            ],
        ],
        [
            [{"text": ""}, [{"text": "Olá"}, {"text": "Mundo"}]],
            [
                {
                    "children": [{"text": ""}, {"text": "Olá"}, {"text": "Mundo"}],
                    "type": "p",
                }
            ],
        ],
    ],
)
def test_process_top_level_items(raw_value: list, expected: list):
    func = slate.process_top_level_items
    result = func(raw_value)
    assert isinstance(result, list)
    assert result == expected

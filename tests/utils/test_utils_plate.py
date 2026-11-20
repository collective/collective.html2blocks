from collective.html2blocks.utils import plate
from copy import deepcopy

import pytest


VALUE = [{"type": "p", "children": [{"text": "Hi"}], "blockWidth": "default"}]
CONTENT = {"blocks": {"a": {"@type": "title"}}, "blocks_layout": {"items": ["a"]}}
UNKNOWN_FORMATS = ["legacy", "", "Main", "plate", "__somersault__"]


def test_migrate_value(traverse, name, value, path, expected):
    result = traverse(plate.migrate_value(value), path)
    assert result == expected, f"{name}: {result} != {expected}"


def test_nodes_from_block(traverse, name, block, title, path, expected):
    result = traverse(plate.nodes_from_block(block, title), path)
    assert result == expected, f"{name}: {result} != {expected}"


def test_migrate_content(traverse, name, content, title, plate_format, path, expected):
    kwargs = {} if plate_format is None else {"plate_format": plate_format}
    original = deepcopy(content)
    result = plate.migrate_content(content, title, **kwargs)
    assert content == original, f"{name}: changed the content"
    again = plate.migrate_content(result, title, **kwargs)
    assert again == result, f"{name}: not idempotent"
    for other in plate.PLATE_FORMATS:
        rerun = plate.migrate_content(result, title, other)
        assert rerun == result, f"{name}: migrated again as {other}"
    value = traverse(result, path)
    assert value == expected, f"{name}: {value} != {expected}"


@pytest.mark.parametrize(
    "plate_format,expected",
    [
        ["main", {"@type": "plate", "value": VALUE}],
        ["somersault", {"@type": "__somersault__", "value": VALUE}],
    ],
)
def test_plate_block(plate_format: str, expected: dict):
    assert plate.plate_block(VALUE, plate_format) == expected


def test_plate_block_defaults_to_main():
    assert plate.plate_block(VALUE) == {"@type": "plate", "value": VALUE}


def test_plate_block_keeps_the_value():
    """The value goes in as it is: the block wraps it, and doesn't copy it."""
    value = deepcopy(VALUE)
    assert plate.plate_block(value)["value"] is value


@pytest.mark.parametrize(
    "plate_format,expected",
    [["main", "main"], ["somersault", "__somersault__"]],
)
def test_body_key(plate_format: str, expected: str):
    assert plate.body_key(plate_format) == expected


def test_body_key_defaults_to_main():
    assert plate.body_key() == "main"


def test_body_keys():
    """Every format has its own key, so either one marks migrated content."""
    assert {plate.body_key(f) for f in plate.PLATE_FORMATS} == plate.BODY_KEYS
    assert {"main", "__somersault__"} == plate.BODY_KEYS


def test_default_plate_format():
    assert plate.DEFAULT_PLATE_FORMAT == "main"
    assert plate.PLATE_FORMATS == ("main", "somersault")


@pytest.mark.parametrize(
    "plate_format,key,block_type",
    [
        [None, "main", "plate"],
        ["main", "main", "plate"],
        ["somersault", "__somersault__", "__somersault__"],
    ],
)
def test_info_from_blocks(plate_format: str | None, key: str, block_type: str):
    blocks = [
        {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Hi"}]}]}
    ]
    kwargs = {} if plate_format is None else {"plate_format": plate_format}
    assert plate.info_from_blocks(blocks, **kwargs) == {
        "blocks": {key: {"@type": block_type, "value": VALUE}},
        "blocks_layout": {"items": []},
    }


@pytest.mark.parametrize("plate_format", UNKNOWN_FORMATS)
@pytest.mark.parametrize(
    "call",
    [
        lambda f: plate.check_plate_format(f),
        lambda f: plate.body_key(f),
        lambda f: plate.plate_block(VALUE, f),
        lambda f: plate.info_from_blocks([], "", f),
        lambda f: plate.migrate_content(CONTENT, None, f),
    ],
    ids=[
        "check_plate_format",
        "body_key",
        "plate_block",
        "info_from_blocks",
        "migrate_content",
    ],
)
def test_unknown_plate_format(call, plate_format: str):
    with pytest.raises(ValueError, match=f"^Unsupported Plate format: {plate_format}$"):
        call(plate_format)


@pytest.mark.parametrize(
    "content",
    [
        {"title": "No blocks"},
        {"blocks": {}, "blocks_layout": {"items": []}},
        {"blocks": {"main": {"@type": "plate", "value": []}}, "blocks_layout": {}},
    ],
    ids=["no-blocks", "empty-blocks", "already-migrated"],
)
def test_migrate_content_checks_the_format_before_skipping(content: dict):
    """A content item returned as it is still fails on an unknown format."""
    with pytest.raises(ValueError, match=r"^Unsupported Plate format: legacy$"):
        plate.migrate_content(content, None, "legacy")


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_check_plate_format_accepts_the_formats(plate_format: str):
    assert plate.check_plate_format(plate_format) is None


def test_migrate_value_leaves_the_input():
    value = [{"type": "ul", "children": [{"type": "li", "children": [{"text": "a"}]}]}]
    original = deepcopy(value)
    plate.migrate_value(value)
    assert value == original


def test_nodes_from_block_leaves_the_input():
    block = {"@type": "listing", "querystring": {"criteria": []}}
    original = deepcopy(block)
    plate.nodes_from_block(block)[0]["querystring"]["criteria"].append("x")
    assert block == original

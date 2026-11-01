from collective.html2blocks.utils import plate
from copy import deepcopy


def test_migrate_value(traverse, name, value, path, expected):
    result = traverse(plate.migrate_value(value), path)
    assert result == expected, f"{name}: {result} != {expected}"


def test_nodes_from_block(traverse, name, block, title, path, expected):
    result = traverse(plate.nodes_from_block(block, title), path)
    assert result == expected, f"{name}: {result} != {expected}"


def test_migrate_content(traverse, name, content, title, path, expected):
    original = deepcopy(content)
    result = plate.migrate_content(content, title)
    assert content == original, f"{name}: changed the content"
    assert plate.migrate_content(result, title) == result, f"{name}: not idempotent"
    value = traverse(result, path)
    assert value == expected, f"{name}: {value} != {expected}"


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

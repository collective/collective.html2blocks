from collective.html2blocks import converter


def test_html_to_blocks(traverse, name, src, path, expected):
    result = converter.html_to_blocks(src)
    assert isinstance(result, list)
    if path == "":
        assert result is expected
    else:
        value = traverse(result, path)
        assert value == expected, f"{name}: {value} != {expected}"


def test_volto_blocks(traverse, name, src, default_blocks, path, expected):
    result = converter.volto_blocks(src, default_blocks)
    assert isinstance(result, dict)
    blocks = result["blocks"]
    assert isinstance(blocks, dict)
    blocks_layout = result["blocks_layout"]
    assert isinstance(blocks_layout, dict)
    items = blocks_layout["items"]
    assert isinstance(items, list)
    assert set(items) == set(blocks.keys())

    # Keeping default as first in the list
    for idx, block in enumerate(default_blocks):
        assert block == blocks[items[idx]]

    if path == "":
        assert result is expected
    else:
        value = traverse(result, path)
        assert value == expected, f"{name}: {value} != {expected}"

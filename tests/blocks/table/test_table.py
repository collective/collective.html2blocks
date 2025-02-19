def test_table_block(block_factory, traverse, name, src, path, expected):
    result = block_factory(src)
    if path == "":
        # Block is None
        assert result is expected
    else:
        value = traverse(result, path)
        assert value == expected, f"{name}: {value} != {expected}"

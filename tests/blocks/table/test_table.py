def test_table_block(block_factory, traverse, name, src, path, expected):
    results = list(block_factory(src))
    if path == "":
        # Block is None
        assert results is expected
    else:
        value = traverse(results, path)
        assert value == expected, f"{name}: {value} != {expected}"

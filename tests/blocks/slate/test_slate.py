def test_slate_block(block_factory, traverse, name, src, path, expected):
    results = block_factory(src)
    if path == "":
        # Empty block
        assert results == expected
    else:
        value = traverse(results, path)
        assert value == expected, f"{name}: {value} != {expected}"

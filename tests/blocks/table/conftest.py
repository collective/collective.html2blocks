from collective.html2blocks.blocks import table

import pytest


@pytest.fixture
def source() -> str:
    return "<table><tr><td>A value</td></tr></table>"


@pytest.fixture
def block_factory(tag_from_str):
    def func(source: str) -> dict:
        tag = tag_from_str(source)
        return table.table_block(tag)

    return func


@pytest.fixture
def block(source, block_factory):
    return block_factory(source)

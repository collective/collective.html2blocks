from collective.html2blocks.blocks import slate

import pytest


@pytest.fixture
def source() -> str:
    return "<p>Hello World!</p>"


@pytest.fixture
def block_factory(tag_from_str):
    def func(source: str) -> list[dict]:
        tag = tag_from_str(source)
        return slate.slate_block(tag)

    return func


@pytest.fixture
def block(source, block_factory):
    return block_factory(source)

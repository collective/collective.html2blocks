from collective.html2blocks.blocks import iframe

import pytest


@pytest.fixture
def source() -> str:
    return '<iframe width="480" height="270" src="https://www.youtube.com/embed/nAybBXMWPz8?feature=oembed" allowfullscreen></iframe>'


@pytest.fixture
def block_factory(tag_from_str):
    def func(source: str) -> list[dict]:
        tag = tag_from_str(source)
        return iframe.iframe_block(tag)

    return func


@pytest.fixture
def block(source, block_factory):
    return block_factory(source)

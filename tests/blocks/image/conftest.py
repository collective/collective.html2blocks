from collective.html2blocks.blocks import image

import pytest


@pytest.fixture
def source() -> str:
    return '<img src="https://plone.org/news/item/@@images/image/thumb" title="A Picture" alt="Picture of a person" class="image-right">'


@pytest.fixture
def block_factory(tag_from_str):
    def func(source: str) -> list[dict]:
        tag = tag_from_str(source)
        return image.image_block(tag)

    return func


@pytest.fixture
def block(source, block_factory):
    return block_factory(source)

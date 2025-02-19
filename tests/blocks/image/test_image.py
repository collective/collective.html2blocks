from collective.html2blocks.blocks import image

import pytest


@pytest.mark.parametrize(
    "css_classes,expected",
    [
        [["image-right"], "right"],
        [["image-left"], "left"],
        [["image-inline"], "center"],
        [["foo", "bar"], "center"],
        [[], "center"],
    ],
)
def test__align_from_classes(css_classes, expected):
    func = image._align_from_classes
    assert func(css_classes) == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        [
            "https://plone.org/news/item/@@images/f392049f-b5ba-4bdc-94c1-525a1314e87f.jpeg",
            "",
        ],
        ["https://plone.org/news/item/@@images/image/thumb", "thumb"],
        ["https://plone.org/news/item/image_thumb", "thumb"],
        ["https://plone.org/news/item/image", "original"],
        ["news/item/image_thumb", "thumb"],
    ],
)
def test__scale_from_src(source, expected):
    func = image._scale_from_src
    assert func(source) == expected


def test_image_block(block_factory, traverse, name, src, path, expected):
    results = block_factory(src)
    if path == "":
        # Empty block
        assert results == expected
    else:
        value = traverse(results, path)
        assert value == expected, f"{name}: {value} != {expected}"

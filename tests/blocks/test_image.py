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


IMG_WITHOUT_SCALE = '<img src="https://plone.org/news/item/@@images/44ae2493-53fb-4221-98dc-98fa38d6851a.jpeg" title="A Picture" alt="Picture of a person" class="image-right">'
IMG_WITH_SCALE = '<img src="https://plone.org/news/item/@@images/image/thumb" title="A Picture" alt="Picture of a person" class="image-right">'
IMG_NO_VIEW = '<img src="https://plone.org/news/item" title="A Picture" alt="Picture of a person" class="lazy-load">'
IMG_RESOLVE_UID = '<img src="../resolveuid/7c6a1b0a0d2f40ffb6a4c73fd67b185d" title="A Picture" alt="Picture of a person" class="lazy-load">'
IMG_DATA_ATTRS = '<img src="../resolveuid/7c6a1b0a0d2f40ffb6a4c73fd67b185d" title="A Picture" alt="Picture of a person" data-align="wide">'


@pytest.mark.parametrize(
    "source,key,expected",
    [
        [IMG_WITHOUT_SCALE, "@type", "image"],
        [IMG_WITHOUT_SCALE, "url", "https://plone.org/news/item"],
        [IMG_WITHOUT_SCALE, "title", "A Picture"],
        [IMG_WITHOUT_SCALE, "alt", "Picture of a person"],
        [IMG_WITHOUT_SCALE, "size", "m"],
        [IMG_WITHOUT_SCALE, "align", "right"],
        [IMG_WITH_SCALE, "@type", "image"],
        [IMG_WITH_SCALE, "url", "https://plone.org/news/item"],
        [IMG_WITH_SCALE, "title", "A Picture"],
        [IMG_WITH_SCALE, "alt", "Picture of a person"],
        [IMG_WITH_SCALE, "size", "s"],
        [IMG_WITH_SCALE, "align", "right"],
        [IMG_NO_VIEW, "@type", "image"],
        [IMG_NO_VIEW, "url", "https://plone.org/news/item"],
        [IMG_NO_VIEW, "title", "A Picture"],
        [IMG_NO_VIEW, "alt", "Picture of a person"],
        [IMG_NO_VIEW, "size", "l"],
        [IMG_NO_VIEW, "align", "center"],
        [IMG_RESOLVE_UID, "@type", "image"],
        [IMG_RESOLVE_UID, "url", "../resolveuid/7c6a1b0a0d2f40ffb6a4c73fd67b185d"],
        [IMG_RESOLVE_UID, "title", "A Picture"],
        [IMG_RESOLVE_UID, "alt", "Picture of a person"],
        [IMG_RESOLVE_UID, "size", "l"],
        [IMG_RESOLVE_UID, "align", "center"],
        [IMG_DATA_ATTRS, "@type", "image"],
        [IMG_DATA_ATTRS, "url", "../resolveuid/7c6a1b0a0d2f40ffb6a4c73fd67b185d"],
        [IMG_DATA_ATTRS, "title", "A Picture"],
        [IMG_DATA_ATTRS, "alt", "Picture of a person"],
        [IMG_DATA_ATTRS, "size", "l"],
        [IMG_DATA_ATTRS, "align", "wide"],
    ],
)
def test_image_block(tag_from_str, source: str, key: str, expected: str):
    func = image.image_block
    element = tag_from_str(source)
    results = func(element)
    assert isinstance(results, list)
    result = results[0]
    assert isinstance(result, dict)
    assert result[key] == expected

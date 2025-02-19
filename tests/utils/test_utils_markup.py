from collective.html2blocks.utils import markup

import pytest


@pytest.mark.parametrize(
    "src,filter_,group,expected",
    [
        [
            "<div><p>Hello World!</p></div>",
            False,
            False,
            "<div><p>Hello World!</p></div>",
        ],
        ["<div><p>Hello World!</p></div>", True, True, "<p>Hello World!</p>"],
        ["<b>Hello</b> World!", True, True, "<p><b>Hello</b> World!</p>"],
        ["<b>Hello</b> World!", False, False, "<b>Hello</b> World!"],
    ],
)
def test_parse_source(src: str, filter_: bool, group: bool, expected: str):
    func = markup.parse_source
    result = func(src, filter_, group)
    assert str(result) == expected


@pytest.mark.parametrize(
    "src,style,expected",
    [
        ['<span style="font-weight: bold;">Bold Text</span>', "font-weight", "bold"],
        ['<span style="font-weight:bold;">Bold Text</span>', "font-weight", "bold"],
        ['<span style="font-style:italic;">Em Text</span>', "font-style", "italic"],
        [
            '<span style="font-style: italic;">Em Text</span>',
            "font-style",
            "italic",
        ],
        [
            '<span style="vertical-align:sub;font-weight:bold;">Bold Sub Text</span>',
            "vertical-align",
            "sub",
        ],
        [
            '<span style="vertical-align:sub;font-weight:bold;">Bold Sub Text</span>',
            "font-weight",
            "bold",
        ],
        [
            '<span style="vertical-align:sub; font-weight: bold;">Bold Sub Text</span>',
            "vertical-align",
            "sub",
        ],
        [
            '<span style="vertical-align: sub;\nfont-weight: bold;">Bold Sub Text</span>',
            "font-weight",
            "bold",
        ],
    ],
)
def test_styles(tag_from_str, src, style, expected):
    func = markup.styles
    element = tag_from_str(src)
    result = func(element)
    assert result.get(style) == expected

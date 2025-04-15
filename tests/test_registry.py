from collections.abc import Callable
from collective.html2blocks import registry
from contextlib import nullcontext as does_not_raise

import pytest


IFRAME_SRC = """<iframe width="480" height="270" src="https://youtube.com/embed/nAybBXMWPz8" />"""


@pytest.mark.parametrize(
    "src,tag_name,strict,expectation,type_",
    [
        ["", "", True, pytest.raises(RuntimeError), None],
        ["<img />", "", True, does_not_raise(), Callable],
        ["", "img", True, does_not_raise(), Callable],
        ["<table></table>", "", True, does_not_raise(), Callable],
        ["", "table", True, does_not_raise(), Callable],
        ["<video />", "", True, does_not_raise(), Callable],
        ["", "video", True, does_not_raise(), Callable],
        ["<p>Hello</p>", "", True, does_not_raise(), None],
        ["<p>Hello</p>", "", False, does_not_raise(), Callable],
        [IFRAME_SRC, "", True, does_not_raise(), Callable],
        [IFRAME_SRC, "", False, does_not_raise(), Callable],
    ],
)
def test_get_block_converter(
    tag_from_str, src: str, tag_name: str, strict: bool, expectation, type_
):
    func = registry.get_block_converter
    element = tag_from_str(src) if src else None
    with expectation:
        converter = func(element, tag_name, strict=strict)
        if type_:
            assert isinstance(converter, type_)
        else:
            assert converter is type_


@pytest.mark.parametrize(
    "src,tag_name,expectation",
    [
        ["", "", pytest.raises(RuntimeError)],
        ["<p>Foo</p>", "", does_not_raise()],
        ["", "p", does_not_raise()],
        ["<span>Foo</span>", "", does_not_raise()],
        ["", "span", does_not_raise()],
        ["<div>Foo</div>", "", does_not_raise()],
        ["", "div", does_not_raise()],
    ],
)
def test_get_element_converter(tag_from_str, src: str, tag_name: str, expectation):
    func = registry.get_element_converter
    element = tag_from_str(src) if src else None
    with expectation:
        converter = func(element, tag_name)
        assert isinstance(converter, Callable)


def test_report_registrations():
    func = registry.report_registrations
    result = func()
    assert isinstance(result, dict)
    assert "block" in result
    assert "*" in result["block"]
    assert "element" in result
    assert "iframe" in result

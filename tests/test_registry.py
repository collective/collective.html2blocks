from collections.abc import Callable
from collective.html2blocks import converter
from collective.html2blocks import registry
from contextlib import nullcontext as does_not_raise

import copy
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


@pytest.fixture
def restore_registry():
    """Restore the block types and tag bindings changed by a test."""
    reg = registry._REGISTRY
    types = {name: copy.deepcopy(item) for name, item in reg.block_types.items()}
    tags = dict(reg.tag_block_types)
    converters = dict(reg.block_converters)
    yield reg
    reg.block_types.clear()
    reg.block_types.update(types)
    reg.tag_block_types.clear()
    reg.tag_block_types.update(tags)
    reg.block_converters.clear()
    reg.block_converters.update(converters)
    registry._DEFAULT_BLOCKS.clear()


def _report() -> dict[str, dict]:
    return {item["block_type"]: item for item in registry.report_blocks()}


@pytest.mark.parametrize(
    "block_type,package,enabled,required,tags,providers",
    [
        ["codeBlock", "@plonegovbr/volto-code-block", False, False, ["pre"], []],
        ["iframe", "@kitconcept/volto-iframe-block", True, False, [], ["iframe"]],
        ["image", "@plone/volto", True, False, ["img"], []],
        ["maps", "@plone/volto", True, False, [], ["googlemaps"]],
        ["slate", "@plone/volto", True, True, [], []],
        ["slateTable", "@plone/volto", True, False, ["table"], []],
        [
            "soundcloudBlock",
            "@kitconcept/volto-social-blocks",
            True,
            False,
            [],
            ["soundcloud"],
        ],
        ["video", "@plone/volto", True, False, ["video"], ["vimeo", "youtube"]],
    ],
)
def test_report_blocks(
    block_type: str,
    package: str,
    enabled: bool,
    required: bool,
    tags: list,
    providers: list,
):
    item = _report()[block_type]
    assert item["package"] == package
    assert item["enabled"] is enabled
    assert item["required"] is required
    assert item["tags"] == tags
    assert item["providers"] == providers
    assert item["description"]


def test_report_blocks_lists_every_block_type():
    assert list(_report()) == [
        "codeBlock",
        "iframe",
        "image",
        "maps",
        "slate",
        "slateTable",
        "soundcloudBlock",
        "video",
    ]


def test_report_blocks_options():
    assert _report()["codeBlock"]["options"] == [
        {"name": "style", "type": "str", "default": "dark"},
        {"name": "wrapLongLines", "type": "bool", "default": True},
        {"name": "showLineNumbers", "type": "bool", "default": False},
    ]
    assert _report()["image"]["options"] == []


def test_resolve_blocks_defaults():
    resolved = registry.resolve_blocks()
    assert "codeBlock" not in resolved.enabled
    assert resolved.enabled == {
        "iframe",
        "image",
        "maps",
        "slate",
        "slateTable",
        "soundcloudBlock",
        "video",
    }
    assert resolved.options == {}


def test_resolve_blocks_enables_with_options():
    resolved = registry.resolve_blocks({"codeBlock": {"style": "light"}})
    assert "codeBlock" in resolved.enabled
    options = resolved.options["codeBlock"]
    assert (options.style, options.wrapLongLines) == ("light", True)


@pytest.mark.parametrize(
    "setting,match",
    [
        [{"accordion": True}, "Unknown block type accordion"],
        [{"slate": False}, "slate cannot be disabled"],
        [{"image": {"size": "l"}}, "image has no options"],
        [{"video": None}, "must be true, false or a dict"],
    ],
)
def test_resolve_blocks_invalid(setting: dict, match: str):
    with pytest.raises(ValueError, match=match):
        registry.resolve_blocks(setting)


def test_resolve_blocks_empty_dict_enables_with_defaults():
    resolved = registry.resolve_blocks({"codeBlock": {}})
    assert resolved.options["codeBlock"].style == "dark"


def test_conversion_scopes_the_setting():
    assert not registry.is_enabled("codeBlock")
    with registry.conversion({"codeBlock": True, "video": False}) as resolved:
        assert registry.is_enabled("codeBlock")
        assert not registry.is_enabled("video")
        assert registry.block_options("codeBlock") is resolved.options["codeBlock"]
    assert not registry.is_enabled("codeBlock")
    assert registry.is_enabled("video")
    assert registry.block_options("codeBlock") is None


def _types(source: str, blocks: dict | None = None) -> list[str]:
    return [item["@type"] for item in converter.html_to_blocks(source, blocks=blocks)]


TABLE = "<p>a</p><table><tr><td>x</td></tr></table>"
YOUTUBE = '<iframe src="https://www.youtube.com/embed/nAybBXMWPz8"></iframe>'
SOUNDCLOUD = (
    '<iframe src="https://w.soundcloud.com/player/?url=https%3A//'
    'api.soundcloud.com/tracks/123456&color=ff5500"></iframe>'
)
OTHER_IFRAME = '<iframe src="https://example.org/embed"></iframe>'
MAPS = '<iframe src="https://www.google.com/maps/embed?pb=1"></iframe>'
VIMEO = '<iframe src="https://player.vimeo.com/video/76979871"></iframe>'


@pytest.mark.parametrize(
    "source,blocks,expected",
    [
        [TABLE, None, ["slate", "slateTable"]],
        [TABLE, {"slateTable": False}, ["slate", "slate"]],
        [YOUTUBE, None, ["video"]],
        [YOUTUBE, {"video": False}, ["iframe"]],
        [YOUTUBE, {"video": False, "iframe": False}, []],
        [SOUNDCLOUD, None, ["soundcloudBlock"]],
        [SOUNDCLOUD, {"soundcloudBlock": False}, ["iframe"]],
        [OTHER_IFRAME, None, ["iframe"]],
        [OTHER_IFRAME, {"iframe": False}, []],
        [OTHER_IFRAME, {"soundcloudBlock": False}, ["iframe"]],
        [MAPS, None, ["maps"]],
        [MAPS, {"maps": False}, ["iframe"]],
        [VIMEO, None, ["video"]],
        [VIMEO, {"video": False}, ["iframe"]],
    ],
)
def test_disabled_block_types(source: str, blocks: dict | None, expected: list):
    assert _types(source, blocks) == expected


def test_disabled_block_type_uses_fallback(restore_registry):
    def image_link(element):
        yield {"@type": "slate", "plaintext": element["src"]}

    restore_registry.block_types["image"].fallback = image_link
    source = '<img src="https://example.org/i.png">'
    assert _types(source) == ["image"]
    blocks = converter.html_to_blocks(source, blocks={"image": False})
    assert blocks == [{"@type": "slate", "plaintext": "https://example.org/i.png"}]
    with registry.conversion({"image": False}):
        assert registry.get_block_converter(tag_name="img") is image_link
        assert "img" in registry.elements_with_block_converters()


def test_register_block_type_needs_package(restore_registry):
    with pytest.raises(ValueError, match="needs a package"):
        registry.register_block_type("accordion")


@pytest.mark.parametrize(
    "kwargs,match",
    [
        [{"package": "@plone/volto"}, "package='@plonegovbr/volto-code-block'"],
        [{"enabled": True}, "enabled=False"],
        [{"options": dict}, "options="],
    ],
)
def test_register_block_type_conflicts(restore_registry, kwargs: dict, match: str):
    with pytest.raises(ValueError, match=match):
        registry.register_block_type("codeBlock", **kwargs)


def test_register_block_type_completes_metadata(restore_registry):
    registry.register_block_type("accordion", package="@example/volto-accordion")
    item = registry.register_block_type("accordion", description="Accordions.")
    assert item.package == "@example/volto-accordion"
    assert item.description == "Accordions."
    assert item.enabled is True


def test_block_converter_rebinds_tag(restore_registry):
    @registry.block_converter(
        "pre", block_type="accordion", package="@example/volto-accordion"
    )
    def accordion(element):
        yield {"@type": "accordion"}

    assert _report()["accordion"]["tags"] == ["pre"]
    assert _report()["codeBlock"]["tags"] == []
    assert _types("<pre>x</pre>") == ["accordion"]


@pytest.mark.parametrize(
    "key,raw,expected",
    [
        ["style", "light", "light"],
        ["showLineNumbers", "yes", True],
        ["showLineNumbers", "On", True],
        ["wrapLongLines", "false", False],
        ["wrapLongLines", "0", False],
    ],
)
def test_coerce_option_value(key: str, raw: str, expected):
    assert registry.coerce_option_value("codeBlock", key, raw) == expected


@pytest.mark.parametrize(
    "block_type,key,raw,match",
    [
        ["accordion", "style", "x", "Unknown block type accordion"],
        ["image", "size", "l", "image has no options"],
        ["codeBlock", "theme", "x", "Unknown option theme"],
        ["codeBlock", "wrapLongLines", "maybe", "must be a boolean"],
    ],
)
def test_coerce_option_value_invalid(block_type: str, key: str, raw: str, match):
    with pytest.raises(ValueError, match=match):
        registry.coerce_option_value(block_type, key, raw)

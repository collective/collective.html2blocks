from collective.html2blocks import converter
from collective.html2blocks.utils import plate
from pathlib import Path

import pytest
import yaml


FIXTURES = (
    "test_html_to_blocks",
    "test_iframe_block",
    "test_image_block",
    "test_slate_block",
    "test_table_block",
)

# Slate types that must not reach a Plate value.
SLATE_TYPES = {*plate.MARKS, *plate.LIST_STYLES, "link", "pre"}


def _fixture_sources() -> list[str]:
    """Return the source of every case of the Slate fixtures."""
    data_path = Path(__file__).parents[1] / "_data"
    sources = set()
    for fixture in FIXTURES:
        data = yaml.safe_load((data_path / f"{fixture}.yml").read_text())
        sources.update(entry["src"] for entry in data["params"])
    return sorted(sources)


SOURCES = _fixture_sources()


def _walk(nodes: list):
    for node in nodes:
        yield node
        yield from _walk(node.get("children", []))


def _value(result: list) -> list:
    assert len(result) == 1
    assert result[0]["@type"] == "__somersault__"
    return result[0]["value"]


def test_html_to_plate(traverse, name, src, path, expected):
    value = traverse(_value(converter.html_to_blocks(src, converter="plate")), path)
    assert value == expected, f"{name}: {value} != {expected}"


def test_markdown_to_plate(traverse, name, src, path, expected):
    result = converter.markdown_to_blocks(src, converter="plate")
    value = traverse(_value(result), path)
    assert value == expected, f"{name}: {value} != {expected}"


def test_volto_blocks_plate(
    traverse, name, src, default_blocks, additional_blocks, title, path, expected
):
    result = converter.volto_blocks(
        src, default_blocks, additional_blocks, converter="plate", title=title
    )
    value = traverse(result, path)
    assert value == expected, f"{name}: {value} != {expected}"


def test_fixture_sources_found():
    assert len(SOURCES) > 100


@pytest.mark.parametrize(
    "src", SOURCES, ids=[f"{idx:03}" for idx in range(len(SOURCES))]
)
def test_fixture_sources_to_plate(src: str):
    """Every source of the Slate fixtures gives a valid and stable Plate value."""
    value = _value(converter.html_to_blocks(src, converter="plate"))
    for node in value:
        if node.get("type") != plate.PLONE_BLOCK_TYPE:
            assert node["blockWidth"] in plate.BLOCK_WIDTHS, node
    for node in _walk(value):
        assert node.get("type") not in SLATE_TYPES, node
        assert node.get("children") != [], node
        assert "text" in node or "children" in node, node
    assert plate.migrate_value(value) == value


def test_slate_stays_the_default():
    html = "<h1>Hi</h1><pre>ls</pre>"
    assert converter.html_to_blocks(html) == converter.html_to_blocks(
        html, converter="slate"
    )
    assert {block["@type"] for block in converter.html_to_blocks(html)} == {"slate"}


@pytest.mark.parametrize(
    "func",
    [
        converter.html_to_blocks,
        converter.markdown_to_blocks,
        converter.volto_blocks,
    ],
)
def test_unknown_converter(func):
    with pytest.raises(ValueError, match="Unsupported converter: draftjs"):
        func("<p>Hi</p>", converter="draftjs")


def test_plate_respects_a_disabled_code_block():
    html = '<pre><code class="language-py">ls</code></pre>'
    enabled = _value(converter.html_to_blocks(html, converter="plate"))
    assert enabled[0]["lang"] == "python"
    disabled = _value(
        converter.html_to_blocks(html, converter="plate", blocks={"codeBlock": False})
    )
    assert disabled[0].get("type") != "code_block"


def test_plate_blocks_setting_applies():
    value = _value(
        converter.html_to_blocks(
            "<p>a</p><img src='/i.jpg'>", converter="plate", blocks={"image": False}
        )
    )
    assert [node["type"] for node in value] == ["p"]


def test_slate_to_plate_matches_converter_plate():
    html = "<h1>Hi</h1><p>Hello <strong>world</strong></p>"
    migrated = converter.slate_to_plate(converter.volto_blocks(html))
    expected = converter.volto_blocks(html, converter="plate")
    assert migrated["blocks"]["__somersault__"] == expected["blocks"]["__somersault__"]

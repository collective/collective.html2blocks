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


HTML = "<h1>Hi</h1><p>Hello <strong>world</strong></p>"
MARKDOWN = "# Hi\n\nHello **world**\n"
# Slate blocks have random ids: build the content once, so results compare equal.
SLATE_CONTENT = converter.volto_blocks(HTML)

# Key in ``blocks`` and ``@type`` of the block of the Plate value, per format.
BODY = {"main": ("main", "plate"), "somersault": ("__somersault__", "__somersault__")}

UNKNOWN_FORMATS = ["legacy", "", "Main", "plate", "__somersault__"]


def _value(result: list, block_type: str = "plate") -> list:
    """Return the Plate value of a ``plate`` result, checking its single block."""
    assert len(result) == 1
    assert result[0].keys() == {"@type", "value"}
    assert result[0]["@type"] == block_type
    return result[0]["value"]


def _layout_values(info: dict) -> list:
    """Return the blocks of a ``slate`` result in layout order, without their ids."""
    return [info["blocks"][item] for item in info["blocks_layout"]["items"]]


def test_html_to_plate(traverse, name, src, path, expected):
    value = traverse(_value(converter.html_to_blocks(src, converter="plate")), path)
    assert value == expected, f"{name}: {value} != {expected}"


def test_markdown_to_plate(traverse, name, src, path, expected):
    result = converter.markdown_to_blocks(src, converter="plate")
    value = traverse(_value(result), path)
    assert value == expected, f"{name}: {value} != {expected}"


def test_volto_blocks_plate(
    traverse,
    name,
    src,
    default_blocks,
    additional_blocks,
    title,
    plate_format,
    path,
    expected,
):
    kwargs = {} if plate_format is None else {"plate_format": plate_format}
    result = converter.volto_blocks(
        src, default_blocks, additional_blocks, converter="plate", title=title, **kwargs
    )
    value = traverse(result, path)
    assert value == expected, f"{name}: {value} != {expected}"


def test_fixture_sources_found():
    assert len(SOURCES) > 100


@pytest.mark.parametrize(
    "src", SOURCES, ids=[f"{idx:03}" for idx in range(len(SOURCES))]
)
def test_fixture_sources_to_plate(src: str):
    """
    Every source of the Slate fixtures gives a valid and stable Plate value, and
    the ``somersault`` format wraps the same value in the old block.
    """
    value = _value(converter.html_to_blocks(src, converter="plate"))
    for node in value:
        if node.get("type") != plate.PLONE_BLOCK_TYPE:
            assert node["blockWidth"] in plate.BLOCK_WIDTHS, node
    for node in _walk(value):
        assert node.get("type") not in SLATE_TYPES, node
        assert node.get("children") != [], node
        assert "text" in node or "children" in node, node
    assert plate.migrate_value(value) == value
    legacy = converter.html_to_blocks(src, converter="plate", plate_format="somersault")
    assert legacy == [{"@type": "__somersault__", "value": value}]


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


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_slate_to_plate_matches_converter_plate(plate_format: str):
    key, _ = BODY[plate_format]
    migrated = converter.slate_to_plate(
        converter.volto_blocks(HTML), plate_format=plate_format
    )
    expected = converter.volto_blocks(
        HTML, converter="plate", plate_format=plate_format
    )
    assert migrated["blocks"][key] == expected["blocks"][key]


@pytest.mark.parametrize(
    "call",
    [
        lambda **kw: converter.html_to_blocks(HTML, converter="plate", **kw),
        lambda **kw: converter.markdown_to_blocks(MARKDOWN, converter="plate", **kw),
        lambda **kw: converter.volto_blocks(HTML, converter="plate", **kw),
        lambda **kw: converter.slate_to_plate(SLATE_CONTENT, **kw),
    ],
    ids=["html_to_blocks", "markdown_to_blocks", "volto_blocks", "slate_to_plate"],
)
def test_plate_format_defaults_to_main(call):
    """Leaving ``plate_format`` out is the same as asking for ``main``."""
    assert call() == call(plate_format="main")
    assert "__somersault__" not in str(call())


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_html_to_blocks_plate_format(plate_format: str):
    _, block_type = BODY[plate_format]
    result = converter.html_to_blocks(
        HTML, converter="plate", plate_format=plate_format
    )
    assert _value(result, block_type) == _value(
        converter.html_to_blocks(HTML, converter="plate")
    )


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_markdown_to_blocks_plate_format(plate_format: str):
    _, block_type = BODY[plate_format]
    result = converter.markdown_to_blocks(
        MARKDOWN, converter="plate", plate_format=plate_format
    )
    assert _value(result, block_type) == _value(
        converter.markdown_to_blocks(MARKDOWN, converter="plate")
    )


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_volto_blocks_plate_format(plate_format: str):
    """The format moves the key and the ``@type``, and nothing else."""
    key, block_type = BODY[plate_format]
    result = converter.volto_blocks(HTML, converter="plate", plate_format=plate_format)
    value = converter.volto_blocks(HTML, converter="plate")["blocks"]["main"]["value"]
    assert result == {
        "blocks": {key: {"@type": block_type, "value": value}},
        "blocks_layout": {"items": []},
    }


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_slate_to_plate_plate_format(plate_format: str):
    """The format moves the key and the ``@type``; the Slate blocks stay."""
    key, block_type = BODY[plate_format]
    content = {"title": "Welcome", **converter.volto_blocks(HTML)}
    migrated = converter.slate_to_plate(content, plate_format=plate_format)
    assert set(migrated["blocks"]) == {*content["blocks"], key}
    assert migrated["blocks_layout"] == content["blocks_layout"]
    assert migrated["blocks"][key]["@type"] == block_type
    other = BODY["somersault" if plate_format == "main" else "main"][0]
    assert other not in migrated["blocks"]


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_slate_ignores_plate_format(plate_format: str):
    """With ``slate``, a valid ``plate_format`` changes nothing."""
    assert converter.html_to_blocks(
        HTML, plate_format=plate_format
    ) == converter.html_to_blocks(HTML)
    assert converter.markdown_to_blocks(
        MARKDOWN, plate_format=plate_format
    ) == converter.markdown_to_blocks(MARKDOWN)
    assert _layout_values(
        converter.volto_blocks(HTML, plate_format=plate_format)
    ) == _layout_values(converter.volto_blocks(HTML))


@pytest.mark.parametrize("plate_format", UNKNOWN_FORMATS)
@pytest.mark.parametrize("converter_name", ["plate", "slate"])
@pytest.mark.parametrize(
    "func",
    [
        converter.html_to_blocks,
        converter.markdown_to_blocks,
        converter.volto_blocks,
    ],
)
def test_unknown_plate_format(func, converter_name: str, plate_format: str):
    """An unknown format fails with either converter, so a typo never goes unseen."""
    with pytest.raises(ValueError, match=f"^Unsupported Plate format: {plate_format}$"):
        func("<p>Hi</p>", converter=converter_name, plate_format=plate_format)


@pytest.mark.parametrize("plate_format", UNKNOWN_FORMATS)
def test_slate_to_plate_unknown_plate_format(plate_format: str):
    content = {"blocks": {"a": {"@type": "title"}}, "blocks_layout": {"items": ["a"]}}
    with pytest.raises(ValueError, match=f"^Unsupported Plate format: {plate_format}$"):
        converter.slate_to_plate(content, plate_format=plate_format)


def test_unknown_converter_is_reported_before_the_plate_format():
    with pytest.raises(ValueError, match=r"^Unsupported converter: draftjs$"):
        converter.html_to_blocks("<p>Hi</p>", converter="draftjs", plate_format="x")


def test_plate_formats():
    assert converter.PLATE_FORMATS == ("main", "somersault")

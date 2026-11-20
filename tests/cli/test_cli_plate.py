from collective.html2blocks.cli import app
from typer.testing import CliRunner

import json
import pytest
import re


runner = CliRunner()

CONTENT = {
    "title": "Welcome",
    "blocks": {
        "a": {"@type": "title"},
        "b": {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Hi"}]}]},
    },
    "blocks_layout": {"items": ["a", "b"]},
}


HI_VALUE = [{"type": "p", "children": [{"text": "Hi"}], "blockWidth": "default"}]

# Key in ``blocks`` and ``@type`` of the block of the Plate value, per format.
BODY = {"main": ("main", "plate"), "somersault": ("__somersault__", "__somersault__")}


def _plate_value(data: dict, plate_format: str = "main") -> list:
    key, block_type = BODY[plate_format]
    assert data["blocks"][key]["@type"] == block_type
    return data["blocks"][key]["value"]


def _read(path) -> dict:
    return json.loads(path.read_text())


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _plain(output: str) -> str:
    """Return the output without the ANSI colors of a terminal that forces them."""
    return ANSI.sub("", output)


def test_cli_convert_slate_is_the_default(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    result = runner.invoke(app, ["convert", "page.html", "page.json"])
    assert result.exit_code == 0, result.output
    data = json.loads((test_dir / "page.json").read_text())
    assert "__somersault__" not in data["blocks"]
    assert "main" not in data["blocks"]


def test_cli_convert_plate(test_dir):
    (test_dir / "page.md").write_text("Hello **world**\n")
    args = ["convert", "--converter", "plate", "page.md", "page.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    data = json.loads((test_dir / "page.json").read_text())
    assert data["blocks_layout"] == {"items": []}
    assert list(data["blocks"]) == ["main"]
    assert _plate_value(data) == [
        {
            "type": "p",
            "children": [{"text": "Hello "}, {"text": "world", "bold": True}],
            "blockWidth": "default",
        }
    ]


def test_cli_convert_plate_title(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--converter", "plate", "--title", "Welcome"]
    result = runner.invoke(app, [*args, "page.html", "page.json"])
    assert result.exit_code == 0, result.output
    value = _plate_value(json.loads((test_dir / "page.json").read_text()))
    assert [node["type"] for node in value] == ["title", "p"]
    assert value[0]["children"] == [{"text": "Welcome"}]


def test_cli_convert_title_needs_plate(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--title", "Welcome", "page.html", "page.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 2
    assert "--title needs --converter plate" in result.output
    assert not (test_dir / "page.json").exists()


def test_cli_convert_unknown_converter(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--converter", "draftjs", "page.html", "page.json"]
    assert runner.invoke(app, args).exit_code == 2
    assert not (test_dir / "page.json").exists()


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_cli_convert_plate_format(test_dir, plate_format: str):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--converter", "plate", "--plate-format", plate_format]
    result = runner.invoke(app, [*args, "page.html", "page.json"])
    assert result.exit_code == 0, result.output
    key, block_type = BODY[plate_format]
    assert _read(test_dir / "page.json") == {
        "blocks": {key: {"@type": block_type, "value": HI_VALUE}},
        "blocks_layout": {"items": []},
    }


def test_cli_convert_plate_format_defaults_to_main(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    base = ["convert", "--converter", "plate"]
    assert runner.invoke(app, [*base, "page.html", "default.json"]).exit_code == 0
    args = [*base, "--plate-format", "main", "page.html", "main.json"]
    assert runner.invoke(app, args).exit_code == 0
    assert _read(test_dir / "default.json") == _read(test_dir / "main.json")
    assert list(_read(test_dir / "default.json")["blocks"]) == ["main"]


def test_cli_convert_plate_format_with_title(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--converter", "plate", "--plate-format", "somersault"]
    args += ["--title", "Welcome", "page.html", "page.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    value = _plate_value(_read(test_dir / "page.json"), "somersault")
    assert [node["type"] for node in value] == ["title", "p"]
    assert value[0]["children"] == [{"text": "Welcome"}]


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_cli_convert_plate_format_needs_plate(test_dir, plate_format: str):
    """Like ``--title``, the option is refused without ``--converter plate``."""
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--plate-format", plate_format, "page.html", "page.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 2
    assert "--plate-format needs --converter plate" in result.output
    assert not (test_dir / "page.json").exists()


def test_cli_convert_plate_format_needs_plate_with_slate_explicit(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--converter", "slate", "--plate-format", "main"]
    result = runner.invoke(app, [*args, "page.html", "page.json"])
    assert result.exit_code == 2
    assert "--plate-format needs --converter plate" in result.output


@pytest.mark.parametrize("plate_format", ["legacy", "plate", "__somersault__"])
def test_cli_convert_unknown_plate_format(test_dir, plate_format: str):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    args = ["convert", "--converter", "plate", "--plate-format", plate_format]
    result = runner.invoke(app, [*args, "page.html", "page.json"])
    assert result.exit_code == 2
    assert "--plate-format" in _plain(result.output)
    assert not (test_dir / "page.json").exists()


def test_cli_slate2plate(test_dir):
    (test_dir / "page.json").write_text(json.dumps(CONTENT))
    result = runner.invoke(app, ["slate2plate", "page.json", "plate.json"])
    assert result.exit_code == 0, result.output
    assert "Converted page.json" in result.output
    data = json.loads((test_dir / "plate.json").read_text())
    assert set(data["blocks"]) == {"a", "b", "main"}
    assert data["blocks_layout"] == CONTENT["blocks_layout"]
    value = _plate_value(data)
    assert [node["type"] for node in value] == ["title", "p"]
    assert value[0]["children"] == [{"text": "Welcome"}]


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_cli_slate2plate_plate_format(test_dir, plate_format: str):
    (test_dir / "page.json").write_text(json.dumps(CONTENT))
    args = ["slate2plate", "--plate-format", plate_format, "page.json", "plate.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    data = _read(test_dir / "plate.json")
    key, _ = BODY[plate_format]
    assert set(data["blocks"]) == {"a", "b", key}
    value = _plate_value(data, plate_format)
    assert [node["type"] for node in value] == ["title", "p"]


def test_cli_slate2plate_plate_format_defaults_to_main(test_dir):
    (test_dir / "page.json").write_text(json.dumps(CONTENT))
    assert (
        runner.invoke(app, ["slate2plate", "page.json", "default.json"]).exit_code == 0
    )
    args = ["slate2plate", "--plate-format", "main", "page.json", "main.json"]
    assert runner.invoke(app, args).exit_code == 0
    assert _read(test_dir / "default.json") == _read(test_dir / "main.json")


@pytest.mark.parametrize(
    "existing,plate_format",
    [
        ["main", "main"],
        ["main", "somersault"],
        ["somersault", "main"],
        ["somersault", "somersault"],
    ],
)
def test_cli_slate2plate_already_migrated(test_dir, existing: str, plate_format: str):
    """Content with a Plate value in either format is written unchanged."""
    key, block_type = BODY[existing]
    content = {
        **CONTENT,
        "blocks": {**CONTENT["blocks"], key: {"@type": block_type, "value": []}},
    }
    (test_dir / "page.json").write_text(json.dumps(content))
    args = ["slate2plate", "--plate-format", plate_format, "page.json", "plate.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    assert _read(test_dir / "plate.json") == content


@pytest.mark.parametrize("plate_format", ["legacy", "plate", "__somersault__"])
def test_cli_slate2plate_unknown_plate_format(test_dir, plate_format: str):
    (test_dir / "page.json").write_text(json.dumps(CONTENT))
    args = ["slate2plate", "--plate-format", plate_format, "page.json", "plate.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 2
    assert "--plate-format" in _plain(result.output)
    assert not (test_dir / "plate.json").exists()


def test_cli_slate2plate_title(test_dir):
    (test_dir / "page.json").write_text(json.dumps(CONTENT))
    args = ["slate2plate", "--title", "Other", "page.json", "plate.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    value = _plate_value(json.loads((test_dir / "plate.json").read_text()))
    assert value[0]["children"] == [{"text": "Other"}]


def test_cli_slate2plate_missing_source(test_dir):
    result = runner.invoke(app, ["slate2plate", "page.json", "plate.json"])
    assert result.exit_code == 1
    assert "page.json does not exist" in result.output


@pytest.mark.parametrize(
    "source,msg",
    [["{not json", "is not valid JSON"], ["[]", "must hold a JSON object"]],
)
def test_cli_slate2plate_invalid_source(test_dir, source: str, msg: str):
    (test_dir / "page.json").write_text(source)
    result = runner.invoke(app, ["slate2plate", "page.json", "plate.json"])
    assert result.exit_code == 2
    assert msg in result.output
    assert not (test_dir / "plate.json").exists()

from collective.html2blocks.cli import app
from typer.testing import CliRunner

import json
import pytest


runner = CliRunner()

CONTENT = {
    "title": "Welcome",
    "blocks": {
        "a": {"@type": "title"},
        "b": {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Hi"}]}]},
    },
    "blocks_layout": {"items": ["a", "b"]},
}


def _plate_value(data: dict) -> list:
    return data["blocks"]["__somersault__"]["value"]


def test_cli_convert_slate_is_the_default(test_dir):
    (test_dir / "page.html").write_text("<p>Hi</p>")
    result = runner.invoke(app, ["convert", "page.html", "page.json"])
    assert result.exit_code == 0, result.output
    data = json.loads((test_dir / "page.json").read_text())
    assert "__somersault__" not in data["blocks"]


def test_cli_convert_plate(test_dir):
    (test_dir / "page.md").write_text("Hello **world**\n")
    args = ["convert", "--converter", "plate", "page.md", "page.json"]
    result = runner.invoke(app, args)
    assert result.exit_code == 0, result.output
    data = json.loads((test_dir / "page.json").read_text())
    assert data["blocks_layout"] == {"items": ["__somersault__"]}
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


def test_cli_slate2plate(test_dir):
    (test_dir / "page.json").write_text(json.dumps(CONTENT))
    result = runner.invoke(app, ["slate2plate", "page.json", "plate.json"])
    assert result.exit_code == 0, result.output
    assert "Converted page.json" in result.output
    data = json.loads((test_dir / "plate.json").read_text())
    assert set(data["blocks"]) == {"a", "b", "__somersault__"}
    value = _plate_value(data)
    assert [node["type"] for node in value] == ["title", "p"]
    assert value[0]["children"] == [{"text": "Welcome"}]


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

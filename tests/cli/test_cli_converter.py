from collective.html2blocks import converter
from collective.html2blocks.cli import app
from collective.html2blocks.commands.convert import detect_format
from pathlib import Path
from typer.testing import CliRunner

import json
import pytest


runner = CliRunner()

MARKDOWN_SOURCE = "# Title\n\nHello **world**.\n"


def _ordered_blocks(info: dict, strip_keys) -> list:
    """Return the blocks of a Volto info structure in layout order, keys removed."""
    return [strip_keys(info["blocks"][item]) for item in info["blocks_layout"]["items"]]


@pytest.mark.parametrize(
    "filename,expected",
    [
        ["page.md", "markdown"],
        ["page.markdown", "markdown"],
        ["page.MD", "markdown"],
        ["page.html", "html"],
        ["page.htm", "html"],
        ["page", "html"],
    ],
)
def test_cli_detect_format(filename: str, expected: str):
    assert detect_format(Path(filename)) == expected


def test_cli_convert_markdown_suffix(test_dir, strip_keys):
    (test_dir / "page.md").write_text(MARKDOWN_SOURCE)
    result = runner.invoke(app, ["convert", "page.md", "page.json"])
    assert result.exit_code == 0, result.stdout
    data = json.loads((test_dir / "page.json").read_text())
    expected = converter.volto_blocks(MARKDOWN_SOURCE, source_format="markdown")
    assert _ordered_blocks(data, strip_keys) == _ordered_blocks(expected, strip_keys)
    assert _ordered_blocks(data, strip_keys)


def test_cli_convert_format_html_overrides_suffix(test_dir, strip_keys):
    (test_dir / "page.md").write_text(MARKDOWN_SOURCE)
    result = runner.invoke(app, ["convert", "--format", "html", "page.md", "page.json"])
    assert result.exit_code == 0, result.stdout
    data = json.loads((test_dir / "page.json").read_text())
    expected = converter.volto_blocks(MARKDOWN_SOURCE)
    assert _ordered_blocks(data, strip_keys) == _ordered_blocks(expected, strip_keys)
    as_markdown = converter.volto_blocks(MARKDOWN_SOURCE, source_format="markdown")
    assert _ordered_blocks(data, strip_keys) != _ordered_blocks(as_markdown, strip_keys)


def test_cli_convert_format_markdown_overrides_suffix(test_dir, strip_keys):
    (test_dir / "page.html").write_text(MARKDOWN_SOURCE)
    result = runner.invoke(
        app, ["convert", "--format", "markdown", "page.html", "page.json"]
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads((test_dir / "page.json").read_text())
    expected = converter.volto_blocks(MARKDOWN_SOURCE, source_format="markdown")
    assert _ordered_blocks(data, strip_keys) == _ordered_blocks(expected, strip_keys)


def test_cli_convert_invalid_format(test_dir):
    (test_dir / "page.md").write_text(MARKDOWN_SOURCE)
    result = runner.invoke(app, ["convert", "--format", "rst", "page.md", "page.json"])
    assert result.exit_code != 0
    assert not (test_dir / "page.json").exists()


@pytest.mark.parametrize(
    "src,dst,exit_code,msg",
    [
        ["valid.html", "valid.json", 0, "Converted"],
        ["invalid.html", "valid.json", 1, "invalid.html does not exist"],
    ],
)
def test_cli_converter(html_dir, src: str, dst: str, exit_code: int, msg: str):
    payload = [
        "convert",
        f"{html_dir}/{src}",
        f"{html_dir}/{dst}",
    ]
    result = runner.invoke(app, payload)
    assert result.exit_code == exit_code
    assert msg in result.stdout

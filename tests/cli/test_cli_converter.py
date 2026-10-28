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


def test_cli_converter_missing_source_exits_cleanly(html_dir):
    """
    A missing source file stops the command at the path check.

    The error is reported and the command exits with code 1 without reaching
    the read step, so no FileNotFoundError traceback is raised and no output
    file is written.

    :param html_dir: Directory with the sample HTML files, as a Path.
    """
    dst = html_dir / "missing.json"
    payload = [
        "convert",
        f"{html_dir}/missing.html",
        f"{dst}",
    ]
    result = runner.invoke(app, payload)
    assert result.exit_code == 1
    assert "missing.html does not exist" in result.stdout
    assert isinstance(result.exception, SystemExit)
    assert not isinstance(result.exception, FileNotFoundError)
    assert not dst.exists()


def test_cli_convert_code_block_option(test_dir, strip_keys):
    (test_dir / "page.md").write_text(MARKDOWN_SOURCE + "\n```py\nx = 1\n```\n")
    result = runner.invoke(app, ["convert", "--code-block", "page.md", "page.json"])
    assert result.exit_code == 0, result.stdout
    data = json.loads((test_dir / "page.json").read_text())
    expected = converter.volto_blocks(
        MARKDOWN_SOURCE + "\n```py\nx = 1\n```\n",
        source_format="markdown",
        code_block={},
    )
    assert _ordered_blocks(data, strip_keys) == _ordered_blocks(expected, strip_keys)
    code = [b for b in _ordered_blocks(data, strip_keys) if b["@type"] == "codeBlock"]
    assert code == [
        {
            "@type": "codeBlock",
            "code": "x = 1",
            "language": "python",
            "showLineNumbers": False,
            "lineNbr": 1,
            "style": "dark",
            "wrapLongLines": True,
        }
    ]


def test_cli_convert_code_block_overrides(test_dir):
    (test_dir / "page.md").write_text("```sh\nls\n```\n")
    result = runner.invoke(
        app,
        [
            "convert",
            "--code-block",
            "--code-style",
            "light",
            "--no-wrap-long-lines",
            "--show-line-numbers",
            "page.md",
            "page.json",
        ],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads((test_dir / "page.json").read_text())
    block = next(iter(data["blocks"].values()))
    assert block["style"] == "light"
    assert block["wrapLongLines"] is False
    assert block["showLineNumbers"] is True
    assert block["language"] == "bash"


def test_cli_convert_code_block_off_by_default(test_dir):
    (test_dir / "page.md").write_text("```sh\nls\n```\n")
    result = runner.invoke(app, ["convert", "page.md", "page.json"])
    assert result.exit_code == 0, result.stdout
    data = json.loads((test_dir / "page.json").read_text())
    types = {block["@type"] for block in data["blocks"].values()}
    assert "codeBlock" not in types


def test_cli_convert_code_options_require_code_block(test_dir):
    (test_dir / "page.md").write_text("```sh\nls\n```\n")
    result = runner.invoke(
        app, ["convert", "--code-style", "light", "page.md", "page.json"]
    )
    assert result.exit_code == 2
    assert "require --code-block" in result.stdout
    assert not (test_dir / "page.json").exists()

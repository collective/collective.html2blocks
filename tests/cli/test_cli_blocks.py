from collective.html2blocks import registry
from collective.html2blocks.cli import app
from collective.html2blocks.commands.blocks import render_markdown
from pathlib import Path
from typer.testing import CliRunner

import json
import pytest


runner = CliRunner()

DOCS_PAGE = (
    Path(__file__).parents[2] / "docs" / "docs" / "reference" / "_supported-blocks.md"
)


def test_cli_blocks_json():
    result = runner.invoke(app, ["blocks", "--format", "json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == registry.report_blocks()


@pytest.mark.parametrize(
    "line",
    [
        "codeBlock [off] @plonegovbr/volto-code-block",
        "  from: <pre>",
        '  option style (str, default "dark")',
        "slate [always] @plone/volto",
        "soundcloudBlock [on] @kitconcept/volto-social-blocks",
        "  from: <video>, <iframe> (vimeo), <iframe> (youtube)",
        "maps [on] @plone/volto",
        "  from: <iframe> (googlemaps)",
    ],
)
def test_cli_blocks_text(line: str):
    result = runner.invoke(app, ["blocks"])
    assert result.exit_code == 0, result.output
    assert line in result.stdout.splitlines()


@pytest.mark.parametrize(
    "line",
    [
        "| `codeBlock` | `@plonegovbr/volto-code-block` | off | `<pre>` |",
        "| `iframe` | `@kitconcept/volto-iframe-block` | on | `<iframe>` |",
        "| `video` | `@plone/volto` | on "
        "| `<video>`, `<iframe> (vimeo)`, `<iframe> (youtube)` |",
        "| `maps` | `@plone/volto` | on | `<iframe> (googlemaps)` |",
        "| `slate` | `@plone/volto` | always | — |",
        "| `wrapLongLines` | `bool` | `true` |",
    ],
)
def test_cli_blocks_markdown(line: str):
    result = runner.invoke(app, ["blocks", "--format", "markdown"])
    assert result.exit_code == 0, result.output
    assert line in result.stdout.splitlines()


def test_cli_blocks_markdown_lists_every_block_type():
    lines = runner.invoke(app, ["blocks", "--format", "markdown"]).stdout.splitlines()
    rows = [line for line in lines if line.startswith("| `") and "@" in line]
    assert len(rows) == len(registry.report_blocks())


def test_docs_supported_blocks_page_is_current():
    """The docs page is generated with ``make docs-blocks``; regenerate it."""
    assert DOCS_PAGE.read_text() == render_markdown(registry.report_blocks())

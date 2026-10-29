"""
Blocks command for ``collective.html2blocks`` CLI.

This Typer subcommand reports the Volto block types the converters can produce:
the frontend package that provides each one, whether it is enabled by default,
what it is converted from, and its options. The Markdown output is the
"Supported blocks" page of the documentation.

Example:
    .. code-block:: shell

        uv run html2blocks blocks
        uv run html2blocks blocks --format json
        uv run html2blocks blocks --format markdown
"""

from collective.html2blocks import _types as t
from enum import StrEnum
from typing import Annotated

import json
import typer


app = typer.Typer()


class ReportFormat(StrEnum):
    """Output formats accepted by the ``--format`` option."""

    text = "text"
    json = "json"
    markdown = "markdown"


def block_state(item: t.BlockReport) -> str:
    """
    Return the default state of a block type, as shown in the reports.

    :param item: One entry of the block report.
    :returns: ``always`` for a required block, otherwise ``on`` or ``off``.
    """
    if item["required"]:
        return "always"
    return "on" if item["enabled"] else "off"


def _sources(item: t.BlockReport) -> list[str]:
    sources = [f"<{tag}>" for tag in item["tags"]]
    for provider in item["providers"]:
        # The default iframe provider is named after the tag itself.
        sources.append("<iframe>" if provider == "iframe" else f"<iframe> ({provider})")
    return sources


def _default(value) -> str:
    return json.dumps(value)


def render_text(report: list[t.BlockReport]) -> str:
    """
    Render the block report as plain text.

    :param report: The report from
        :func:`~collective.html2blocks.registry.report_blocks`.
    :returns: One section per block type.
    """
    lines: list[str] = []
    for item in report:
        lines.append(f"{item['block_type']} [{block_state(item)}] {item['package']}")
        if item["description"]:
            lines.append(f"  {item['description']}")
        if sources := _sources(item):
            lines.append(f"  from: {', '.join(sources)}")
        for option in item["options"]:
            lines.append(
                f"  option {option['name']} ({option['type']}, "
                f"default {_default(option['default'])})"
            )
    return "\n".join(lines)


def render_markdown(report: list[t.BlockReport]) -> str:
    """
    Render the block report as a Markdown table, followed by the block options.

    :param report: The report from
        :func:`~collective.html2blocks.registry.report_blocks`.
    :returns: The Markdown text, ending with a newline.
    """
    lines = [
        "| Block type | Package | Default | Converted from |",
        "| --- | --- | --- | --- |",
    ]
    for item in report:
        sources = ", ".join(f"`{source}`" for source in _sources(item)) or "—"
        lines.append(
            f"| `{item['block_type']}` | `{item['package']}` | {block_state(item)} "
            f"| {sources} |"
        )
    for item in report:
        if not item["options"]:
            continue
        lines.extend(["", f"### `{item['block_type']}` options", ""])
        lines.extend(["| Option | Type | Default |", "| --- | --- | --- |"])
        for option in item["options"]:
            lines.append(
                f"| `{option['name']}` | `{option['type']}` "
                f"| `{_default(option['default'])}` |"
            )
    return "\n".join(lines) + "\n"


@app.command(name="blocks")
def blocks_report(
    output_format: Annotated[
        ReportFormat,
        typer.Option("--format", help="Output format: text, json or markdown."),
    ] = ReportFormat.text,
):
    """
    List the Volto block types the converters can produce.

    For each block type, the report gives the frontend package that provides it,
    its default state (``on``, ``off``, or ``always`` for a block that cannot be
    disabled), the HTML tags and iframe providers converted into it, and its
    options with their defaults.

    :param output_format: Output format.

    Example:
        .. code-block:: shell

            uv run html2blocks blocks

        .. code-block:: console

            codeBlock [off] @plonegovbr/volto-code-block
              Code: HTML <pre> and Markdown code fences or indented code.
              from: <pre>
              option style (str, default "dark")
    """
    from collective.html2blocks.registry import report_blocks

    report = report_blocks()
    match output_format:
        case ReportFormat.json:
            typer.echo(json.dumps(report, indent=2))
        case ReportFormat.markdown:
            typer.echo(render_markdown(report), nl=False)
        case _:
            typer.echo(render_text(report))

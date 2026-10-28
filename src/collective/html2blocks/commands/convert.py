"""
Convert command for ``collective.html2blocks`` CLI.

This Typer subcommand provides functionality to convert HTML or Markdown files to
Volto blocks in JSON format. It checks file paths, reads the input, performs
conversion, and writes the result to the specified output file. The input format is
taken from the file suffix (``.md`` and ``.markdown`` are Markdown) unless
``--format`` says otherwise.

Example:
    .. code-block:: shell

        uv run html2blocks convert input.html output.json
        uv run html2blocks convert input.md output.json
"""

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import json
import typer


app = typer.Typer()

MARKDOWN_SUFFIXES = (".md", ".markdown")


class FormatChoice(StrEnum):
    """Input formats accepted by the ``--format`` option."""

    html = "html"
    markdown = "markdown"


def detect_format(path: Path) -> str:
    """
    Guess the input format of a file from its suffix.

    :param path: The path of the input file.
    :returns: ``"markdown"`` for ``.md`` and ``.markdown`` files, ``"html"`` otherwise.

    Example:
        .. code-block:: pycon

            >>> detect_format(Path('input.md'))
            'markdown'
    """
    if path.suffix.lower() in MARKDOWN_SUFFIXES:
        return "markdown"
    return "html"


def check_path(path: Path) -> bool:
    """
    Check if a file or directory path exists.

    Args:
        path (Path): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.

    Example:
        .. code-block:: pycon

            >>> check_path(Path('input.html'))
            True
    """
    path = path.resolve()
    return path.exists()


def check_paths(src: Path, dst: Path) -> bool:
    """
    Check if both source and destination paths exist, printing errors if not.

    Args:
        src (Path): Source file path.
        dst (Path): Destination directory path.

    Returns:
        bool: True if both exist, False otherwise.
    """
    msgs = []
    if not check_path(src):
        msgs.append(f"{src} does not exist")
    if not check_path(dst):
        msgs.append(f"{dst} does not exist")
    if msgs:
        for msg in msgs:
            typer.echo(msg)
        return False
    return True


@app.command(name="convert")
def convert(
    src: Annotated[Path, typer.Argument(help="Path to the HTML or Markdown file")],
    dst: Annotated[Path, typer.Argument(help="Path to write the JSON conversion")],
    input_format: Annotated[
        FormatChoice | None,
        typer.Option(
            "--format",
            help="Input format: html or markdown. Defaults to the file suffix "
            "(.md and .markdown are Markdown, anything else is HTML).",
        ),
    ] = None,
    code_block: Annotated[
        bool,
        typer.Option(
            "--code-block",
            help="Convert code (<pre> and Markdown fences) to codeBlock blocks. "
            "Off by default, as the codeBlock type comes from an add-on.",
        ),
    ] = False,
    code_style: Annotated[
        str | None,
        typer.Option(
            "--code-style",
            help="Style of the codeBlock blocks (default: dark). "
            "Requires --code-block.",
        ),
    ] = None,
    wrap_long_lines: Annotated[
        bool | None,
        typer.Option(
            "--wrap-long-lines/--no-wrap-long-lines",
            help="Wrap long lines in the codeBlock blocks (default: wrap). "
            "Requires --code-block.",
        ),
    ] = None,
    show_line_numbers: Annotated[
        bool | None,
        typer.Option(
            "--show-line-numbers/--no-show-line-numbers",
            help="Show line numbers in the codeBlock blocks (default: hide). "
            "Requires --code-block.",
        ),
    ] = None,
):
    """
    Convert an HTML or Markdown file to Volto blocks JSON.

    This command reads the file at ``src``, converts its contents to Volto blocks
    using the package's :mod:`~collective.html2blocks.converter`, and writes the
    result as JSON to ``dst``. The input format is detected from the suffix of
    ``src`` unless ``--format`` is given.

    With ``--code-block``, code (``<pre>`` and Markdown fences) becomes
    ``codeBlock`` blocks, and the ``--code-style``, ``--wrap-long-lines`` and
    ``--show-line-numbers`` options override the block defaults.

    :param src: Path to the HTML or Markdown file to convert.
    :param dst: Path to write the JSON output.
    :param input_format: Input format, overriding the suffix detection.
    :param code_block: Convert code into ``codeBlock`` blocks.
    :param code_style: Style of the ``codeBlock`` blocks.
    :param wrap_long_lines: Wrap long lines in the ``codeBlock`` blocks.
    :param show_line_numbers: Show line numbers in the ``codeBlock`` blocks.

    Example:
        .. code-block:: shell

            uv run html2blocks convert input.html output.json
            uv run html2blocks convert input.md output.json
            uv run html2blocks convert --format markdown notes.txt output.json
            uv run html2blocks convert --code-block --code-style light input.md out.json

        .. code-block:: console

            Converted input.html contents into file output.json
    """
    from collective.html2blocks import converter
    from collective.html2blocks.blocks.code import CodeBlockOptions

    dst = dst.resolve()
    folder = dst.parent
    if not check_paths(src, folder):
        raise typer.Exit(1)
    code_options: CodeBlockOptions = {}
    if code_style is not None:
        code_options["style"] = code_style
    if wrap_long_lines is not None:
        code_options["wrapLongLines"] = wrap_long_lines
    if show_line_numbers is not None:
        code_options["showLineNumbers"] = show_line_numbers
    if code_options and not code_block:
        typer.echo(
            "--code-style, --wrap-long-lines and --show-line-numbers "
            "require --code-block"
        )
        raise typer.Exit(2)
    if input_format is None:
        is_markdown = detect_format(src) == "markdown"
    else:
        is_markdown = input_format is FormatChoice.markdown
    source_format: converter.SourceFormat = "markdown" if is_markdown else "html"
    source = src.read_text()
    result = converter.volto_blocks(
        source,
        source_format=source_format,
        code_block=code_options if code_block else None,
    )
    with open(dst, "w") as fout:
        json.dump(result, fout, indent=2)
    typer.echo(f"Converted {src} contents into file {dst}")

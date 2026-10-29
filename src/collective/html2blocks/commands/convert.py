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


def blocks_setting(
    enable: list[str], disable: list[str], options: list[str]
) -> dict[str, bool | dict]:
    """
    Build a ``blocks`` setting from the ``--enable``, ``--disable`` and ``--option``
    values of the command line.

    :param enable: Block types to enable.
    :param disable: Block types to disable.
    :param options: Block options, as ``BLOCK_TYPE.KEY=VALUE``.
    :returns: The ``blocks`` setting, validated against the registry. An option
        enables its block type, as a dict of options does in the setting.
    :raises ValueError: For a malformed option, a block type both enabled and
        disabled, an option of a disabled block type, or anything
        :func:`~collective.html2blocks.registry.resolve_blocks` rejects.

    Example:
        .. code-block:: pycon

            >>> blocks_setting(["codeBlock"], [], ["codeBlock.style=light"])
            {'codeBlock': {'style': 'light'}}
    """
    from collective.html2blocks import registry

    if both := sorted(set(enable) & set(disable)):
        raise ValueError(f"Block types both enabled and disabled: {', '.join(both)}")
    setting: dict[str, bool | dict] = dict.fromkeys(enable, True)
    setting.update(dict.fromkeys(disable, False))
    for item in options:
        name, dot, rest = item.partition(".")
        key, equal, raw = rest.partition("=")
        if not (dot and equal and name and key):
            raise ValueError(f"Option {item} must be BLOCK_TYPE.KEY=VALUE")
        value = registry.coerce_option_value(name, key, raw)
        current = setting.get(name)
        if current is False:
            raise ValueError(f"Option {item} is for a disabled block type")
        setting[name] = {**(current if isinstance(current, dict) else {}), key: value}
    registry.resolve_blocks(setting)
    return setting


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
    enable: Annotated[
        list[str] | None,
        typer.Option(
            "--enable",
            metavar="BLOCK_TYPE",
            help="Enable a block type, such as codeBlock. Repeat for more. "
            "Run 'html2blocks blocks' to list the block types.",
        ),
    ] = None,
    disable: Annotated[
        list[str] | None,
        typer.Option(
            "--disable",
            metavar="BLOCK_TYPE",
            help="Disable a block type, such as slateTable. Repeat for more.",
        ),
    ] = None,
    option: Annotated[
        list[str] | None,
        typer.Option(
            "--option",
            metavar="BLOCK_TYPE.KEY=VALUE",
            help="Set an option of a block type, such as codeBlock.style=light. "
            "The option also enables the block type. Repeat for more.",
        ),
    ] = None,
):
    """
    Convert an HTML or Markdown file to Volto blocks JSON.

    This command reads the file at ``src``, converts its contents to Volto blocks
    using the package's :mod:`~collective.html2blocks.converter`, and writes the
    result as JSON to ``dst``. The input format is detected from the suffix of
    ``src`` unless ``--format`` is given.

    ``--enable`` and ``--disable`` turn block types on and off, and ``--option``
    overrides an option of a block type, enabling it. ``html2blocks blocks`` lists
    the block types with their default state and options.

    :param src: Path to the HTML or Markdown file to convert.
    :param dst: Path to write the JSON output.
    :param input_format: Input format, overriding the suffix detection.
    :param enable: Block types to enable.
    :param disable: Block types to disable.
    :param option: Block options, as ``BLOCK_TYPE.KEY=VALUE``.

    Example:
        .. code-block:: shell

            uv run html2blocks convert input.html output.json
            uv run html2blocks convert input.md output.json
            uv run html2blocks convert --format markdown notes.txt output.json
            uv run html2blocks convert --enable codeBlock \\
                --option codeBlock.style=light input.md out.json
            uv run html2blocks convert --disable slateTable input.html out.json

        .. code-block:: console

            Converted input.html contents into file output.json
    """
    from collective.html2blocks import converter

    dst = dst.resolve()
    folder = dst.parent
    if not check_paths(src, folder):
        raise typer.Exit(1)
    try:
        blocks = blocks_setting(
            list(enable or []), list(disable or []), list(option or [])
        )
    except ValueError as exc:
        typer.echo(str(exc))
        raise typer.Exit(2) from None
    if input_format is None:
        is_markdown = detect_format(src) == "markdown"
    else:
        is_markdown = input_format is FormatChoice.markdown
    source_format: converter.SourceFormat = "markdown" if is_markdown else "html"
    source = src.read_text()
    result = converter.volto_blocks(
        source,
        source_format=source_format,
        blocks=blocks,
    )
    with open(dst, "w") as fout:
        json.dump(result, fout, indent=2)
    typer.echo(f"Converted {src} contents into file {dst}")

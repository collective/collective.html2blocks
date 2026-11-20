"""
Slate to Plate command for ``collective.html2blocks`` CLI.

This Typer subcommand reads a JSON file with a content item in the Volto format,
adds the Plate value that Plone Aurora renders, and writes the result. The value
goes in ``blocks["main"]`` by default, or in ``blocks["__somersault__"]`` with
``--plate-format somersault``, for Aurora sites that have not upgraded yet.

Example:
    .. code-block:: shell

        uv run html2blocks slate2plate page.json plate.json
        uv run html2blocks slate2plate --title Welcome page.json plate.json
        uv run html2blocks slate2plate --plate-format somersault page.json plate.json
"""

from collective.html2blocks.commands.convert import PlateFormatChoice
from pathlib import Path
from typing import Annotated

import json
import typer


app = typer.Typer()


@app.command(name="slate2plate")
def slate2plate(
    src: Annotated[Path, typer.Argument(help="Path to the JSON content item")],
    dst: Annotated[Path, typer.Argument(help="Path to write the migrated JSON")],
    title: Annotated[
        str | None,
        typer.Option(
            "--title",
            help="Text of the title block. Defaults to the title of the content.",
        ),
    ] = None,
    plate_format: Annotated[
        PlateFormatChoice,
        typer.Option(
            "--plate-format",
            help="Where the Plate value goes: main for blocks.main, or "
            "somersault for the __somersault__ block of Aurora sites that have "
            "not upgraded yet.",
        ),
    ] = PlateFormatChoice.main,
):
    """
    Add the Plate value of Plone Aurora to a JSON content item.

    The existing blocks stay, and a content item that already has a ``main`` or
    a ``__somersault__`` block is written unchanged.

    :param src: Path to the JSON file with ``blocks`` and ``blocks_layout`` keys.
    :param dst: Path to write the JSON output.
    :param title: Text of the title block, overriding the title of the content.
    :param plate_format: ``main`` (default) or ``somersault``.

    Example:
        .. code-block:: shell

            uv run html2blocks slate2plate page.json plate.json

        .. code-block:: console

            Converted page.json contents into file plate.json
    """
    from collective.html2blocks.commands.convert import check_paths
    from collective.html2blocks.converter import slate_to_plate

    dst = dst.resolve()
    if not check_paths(src, dst.parent):
        raise typer.Exit(1)
    try:
        content = json.loads(src.read_text())
    except json.JSONDecodeError as exc:
        typer.echo(f"{src} is not valid JSON: {exc}")
        raise typer.Exit(2) from None
    if not isinstance(content, dict):
        typer.echo(f"{src} must hold a JSON object")
        raise typer.Exit(2)
    with open(dst, "w") as fout:
        json.dump(slate_to_plate(content, title, plate_format.value), fout, indent=2)
    typer.echo(f"Converted {src} contents into file {dst}")

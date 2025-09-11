"""
Convert command for collective.html2blocks CLI.

This Typer subcommand provides functionality to convert HTML files to Volto blocks
in JSON format. It checks file paths, reads HTML input, performs conversion, and
writes the result to the specified output file.

Example usage::

    $ uv run html2blocks convert input.html output.json
"""

from pathlib import Path
from typing import Annotated

import json
import typer


app = typer.Typer()


def check_path(path: Path) -> bool:
    """
    Check if a file or directory path exists.

    Args:
        path (Path): The path to check.

    Returns:
        bool: True if the path exists, False otherwise.

    Example::

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
    src: Annotated[Path, typer.Argument(help="Path to the html file")],
    dst: Annotated[Path, typer.Argument(help="Path to write the JSON conversion")],
):
    """
    Convert a HTML file to Volto blocks JSON.

    This command reads the HTML file at `src`, converts its contents to Volto blocks
    using the package's converter, and writes the result as JSON to `dst`.

    Args:
        src (Path): Path to the HTML file to convert.
        dst (Path): Path to write the JSON output.

    Example::

        $ uv run html2blocks convert input.html output.json
        Converted input.html contents into file output.json
    """
    from collective.html2blocks import converter

    dst = dst.resolve()
    folder = dst.parent
    if not check_paths(src, folder):
        typer.Exit(1)
    source = src.read_text()
    result = converter.volto_blocks(source)
    with open(dst, "w") as fout:
        json.dump(result, fout, indent=2)
    typer.echo(f"Converted {src} contents into file {dst}")

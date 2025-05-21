from pathlib import Path
from typing import Annotated

import json
import typer


app = typer.Typer()


def check_path(path: Path) -> bool:
    """Check if path exists."""
    path = path.resolve()
    return path.exists()


def check_paths(src: Path, dst: Path) -> bool:
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
    """Return information about the tool."""
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

from collective.html2blocks.commands.convert import app as app_convert
from collective.html2blocks.commands.info import app as app_info
from collective.html2blocks.commands.server import app as app_server

import typer


app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Welcome to collective.html2blocks."""
    pass


app.add_typer(app_convert)
app.add_typer(app_info)
app.add_typer(app_server)


def cli():
    app()


__all__ = ["cli"]

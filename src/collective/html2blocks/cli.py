from collective.html2blocks.commands.convert import app as app_convert
from collective.html2blocks.commands.info import app as app_info

import typer


app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Welcome to collective.html2blocks."""
    pass


app.add_typer(app_convert)
app.add_typer(app_info)


def cli():
    app()


__all__ = ["cli"]

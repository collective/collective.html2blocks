"""
CLI entry point for ``collective.html2blocks``.

This module provides the Typer-based command-line interface for converting HTML
content to Volto blocks, inspecting conversion info, and running the API server.

Example:
    .. code-block:: shell

        uv run html2blocks convert input.html
        uv run html2blocks info
        uv run html2blocks server
"""

from collective.html2blocks.commands.convert import app as app_convert
from collective.html2blocks.commands.info import app as app_info
from collective.html2blocks.commands.server import app as app_server

import typer


app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    Main CLI callback for ``collective.html2blocks``.

    This function is invoked when the CLI is run without a subcommand. It displays
    a welcome message and help information for available commands.

    Args:
        ctx (typer.Context): Typer context object.

    Example:
        .. code-block:: shell

            $ uv run html2blocks
            Welcome to collective.html2blocks.
    """
    pass


app.add_typer(app_convert)
app.add_typer(app_info)
app.add_typer(app_server)


def cli():
    """
    Run the collective.html2blocks CLI application.

    This function serves as the entry point for the CLI, invoking the Typer app.

    Example:
        .. code-block:: pycon

            >>> cli()
            # Launches the CLI
    """
    app()


__all__ = ["cli"]

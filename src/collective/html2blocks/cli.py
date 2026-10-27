"""
CLI entry point for ``collective.html2blocks``.

The ``html2blocks`` script loads this module. The Typer application lives in
:mod:`collective.html2blocks.cli_app` and needs the ``cli`` extra. When that extra
is missing, :func:`cli` prints one line naming it and exits with status 1.

Example:
    .. code-block:: shell

        uv run html2blocks convert input.html
        uv run html2blocks info
        uv run html2blocks server
"""

from collective.html2blocks.extras import exit_missing_extra
from typing import Any


def cli():
    """
    Run the collective.html2blocks CLI application.

    This function serves as the entry point for the CLI, invoking the Typer app.

    Example:
        .. code-block:: pycon

            >>> cli()
            # Launches the CLI
    """
    try:
        from collective.html2blocks.cli_app import app
    except ModuleNotFoundError as exc:
        if exc.name != "typer":
            raise
        exit_missing_extra("typer", "cli")
    app()


def __getattr__(name: str) -> Any:
    """
    Return the Typer application for code that imports ``app`` from this module.

    :param name: Attribute name requested from the module.
    :returns: The Typer application when ``name`` is ``app``.
    :raises AttributeError: When the module has no attribute called ``name``.
    """
    if name == "app":
        from collective.html2blocks.cli_app import app

        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["cli"]

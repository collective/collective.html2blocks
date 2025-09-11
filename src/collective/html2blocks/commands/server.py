"""
Server command for collective.html2blocks CLI.

This Typer subcommand runs the HTML to Blocks API service using Uvicorn.
It allows you to specify host, port, and reload options for development.

Example usage::

    $ uv run html2blocks server --host 0.0.0.0 --port 8080 --reload
"""

from collective.html2blocks.logger import console_logging
from collective.html2blocks.logger import logger

import typer
import uvicorn


app = typer.Typer()


@app.command(name="server")
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """
    Run the HTML to Blocks API service.

    This command starts a Uvicorn server hosting the FastAPI app for converting
    HTML to Volto blocks. You can customize the host, port, and enable reload
    for development.

    Args:
        host (str, optional): Host address to bind. Defaults to "127.0.0.1".
        port (int, optional): Port to listen on. Defaults to 8000.
        reload (bool, optional): Enable auto-reload for development. Defaults to False.

    Example::

        $ uv run html2blocks server --host 0.0.0.0 --port 8080 --reload
        Starting HTML to Blocks service at http://0.0.0.0:8080
    """
    with console_logging(logger) as log:
        log.info(f"Starting HTML to Blocks service at http://{host}:{port}")
        uvicorn.run(
            "collective.html2blocks.services:app", host=host, port=port, reload=reload
        )

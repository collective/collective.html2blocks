from collective.html2blocks.logger import console_logging
from collective.html2blocks.logger import logger

import typer
import uvicorn


app = typer.Typer()


@app.command(name="server")
def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run the HTML to Blocks service."""
    with console_logging(logger) as log:
        log.info(f"Starting HTML to Blocks service at http://{host}:{port}")
        uvicorn.run(
            "collective.html2blocks.services:app", host=host, port=port, reload=reload
        )

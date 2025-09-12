"""
Info command for ``collective.html2blocks`` CLI.

This Typer subcommand displays information about the tool, including the
package name, version, and registered block and element converters.

Example:
    .. code-block:: shell

        uv run html2blocks info
"""

from collective.html2blocks.logger import console_logging
from collective.html2blocks.logger import logger

import typer


app = typer.Typer()


@app.command(name="info")
def tool_information():
    """
    Show information about the ``collective.html2blocks`` tool and its registrations.

    This command prints the package name, version, and lists all registered block
    and element converters, helping users understand the available conversion logic.

    Example:
        .. code-block:: shell

            uv run html2blocks info

        .. code-block:: console

            # collective.html2blocks - 1.0.0
            ## Block Converters
             - p: module.convert_paragraph
             - div: module.convert_div
            ## Element Converters
             - span: module.convert_span
    """
    from collective.html2blocks import PACKAGE_NAME
    from collective.html2blocks import __version__
    from collective.html2blocks.registry import report_registrations

    registrations = report_registrations()
    with console_logging(logger) as log:
        log.info(f"# {PACKAGE_NAME} - {__version__}")
        log.info("")
        log.info("## Block Converters")
        for tag_name, converter in registrations["block"].items():
            log.info(f" - {tag_name}: {converter}")
        log.info("")
        log.info("## Element Converters")
        for tag_name, converter in registrations["element"].items():
            log.info(f" - {tag_name}: {converter}")

from collective.html2blocks.logger import console_logging
from collective.html2blocks.logger import logger

import typer


app = typer.Typer()


@app.command(name="info")
def tool_information():
    """Return information about the tool."""
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

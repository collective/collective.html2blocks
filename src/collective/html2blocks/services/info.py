"""
Info service for ``collective.html2blocks``.

Provides the root endpoint with basic information about the API service, including
its title, description, and version, and the list of supported block types.

Example:
    .. code-block:: console

        GET /
        Response: {"title": "Blocks Conversion Tool", ...}
        GET /blocks
        Response: [{"block_type": "codeBlock", ...}, ...]
"""

from collective.html2blocks import __version__
from collective.html2blocks import _types as t
from collective.html2blocks.registry import report_blocks
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def root() -> dict:
    """
    Root endpoint for the HTML to Blocks service.

    Returns a JSON object with service metadata including title, description,
    and version.

    Returns:
        dict: Service metadata.

    Example:
        .. code-block:: shell

            curl http://localhost:8000/

        .. code-block:: console

            {"title": "Blocks Conversion Tool",
            "description": "Convert HTML to blocks for use in Volto.",
            "version": "..."}
    """
    return {
        "title": "Blocks Conversion Tool",
        "description": "Convert HTML to blocks for use in Volto.",
        "version": __version__,
    }


@router.get("/blocks")
async def blocks() -> list[t.BlockReport]:
    """
    List the Volto block types the converters can produce.

    Each entry gives the block type, the frontend package that provides it, its
    default state, the tags and iframe providers converted into it, and its
    options with their defaults. Any of them can be enabled, disabled or
    configured with the ``blocks`` field of the conversion endpoints.

    :returns: One report per block type, sorted by block type.

    Example:
        .. code-block:: shell

            curl http://localhost:8000/blocks

        .. code-block:: console

            [{"block_type": "codeBlock", "package": "@plonegovbr/volto-code-block",
              "enabled": false, ...}, ...]
    """
    return report_blocks()

"""
Info service for ``collective.html2blocks``.

Provides the root endpoint with basic information about the API service, including
its title, description, and version.

Example:
    .. code-block:: console

        GET /
        Response: {"title": "Blocks Conversion Tool", ...}
"""

from collective.html2blocks import __version__
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

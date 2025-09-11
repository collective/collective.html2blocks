"""
Healthcheck service for collective.html2blocks.

Provides a simple endpoint to verify that the API service is running and healthy.

Example usage::

    GET /ok
    Response: {"status": "up"}
"""

from fastapi import APIRouter


router = APIRouter()


@router.get("/ok")
async def healthcheck() -> dict:
    """
    Healthcheck endpoint for service status.

    Returns a JSON object indicating the service is up.

    Returns:
        dict: Status information, e.g. {"status": "up"}

    Example::

        $ curl http://localhost:8000/ok
        {"status": "up"}
    """
    return {"status": "up"}

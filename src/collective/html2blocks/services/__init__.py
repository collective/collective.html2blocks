"""
FastAPI application setup for ``collective.html2blocks`` services.

This module initializes the FastAPI app, includes routers for healthcheck,
HTML conversion, and info endpoints, and adds middleware for request timing.

Example:
    .. code-block:: python

        from collective.html2blocks.services import app
        # Use with Uvicorn or other ASGI server
        # uvicorn collective.html2blocks.services:app
"""

from collective.html2blocks import __version__
from collective.html2blocks.services.healthcheck import router as health_router
from collective.html2blocks.services.html import router as html_router
from collective.html2blocks.services.info import router as info_router
from fastapi import FastAPI
from fastapi import Request

import time


app = FastAPI(title="HTML to Blocks Service", version=__version__)

app.include_router(
    info_router,
    tags=["info"],
)
app.include_router(
    html_router,
    tags=["conversion"],
)
app.include_router(
    health_router,
    tags=["health"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to attach ``X-Process-Time`` header to each response.

    This middleware measures the time taken to process each HTTP request and
    adds the result as an ``X-Process-Time`` header in the response.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next ASGI handler to call.

    Returns:
        Response: The HTTP response with the process time header.

    Example:
        .. code-block:: console

            # Response headers will include ``X-Process-Time``
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

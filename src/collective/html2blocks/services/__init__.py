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
    """Attach header with total process time for the request."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

from collective.html2blocks import __version__
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def root() -> dict:
    """Root endpoint for the HTML to Blocks service."""
    return {
        "title": "Blocks Conversion Tool",
        "description": "Convert HTML to blocks for use in Volto.",
        "version": __version__,
    }

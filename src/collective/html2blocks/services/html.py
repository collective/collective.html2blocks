"""
HTML conversion service for collective.html2blocks.

Provides API endpoints for converting HTML content to Volto blocks and block layout
information. Includes endpoints for both simple block conversion and full Volto layout.

Example usage::

    POST /html
    POST /volto
"""

from collective.html2blocks import _types as t
from collective.html2blocks.converter import html_to_blocks
from collective.html2blocks.converter import volto_blocks
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel


router = APIRouter()


class HtmlBody(BaseModel):
    """
    Request body model for HTML to blocks conversion.

    Attributes:
        html (str): The HTML content to convert.
        converter (str): The type of conversion to perform (default is "slate").
    """

    html: str
    converter: str = "slate"


@router.post("/html")
async def convert_html(body: HtmlBody) -> list[t.VoltoBlock]:
    """
    Convert HTML to blocks.

    Converts the provided HTML content to a list of Volto blocks using the specified
    converter.

    Args:
        body (HtmlBody): Request body containing HTML and converter type.

    Returns:
        list[VoltoBlock]: The converted blocks.

    Raises:
        HTTPException: If an unsupported converter is specified.

    Example::

        $ curl -X POST /html -d '{"html": "<p>Hello</p>", "converter": "slate"}'
    """
    converter = body.converter
    html = body.html
    if converter not in ["slate"]:
        raise HTTPException(
            status_code=400, detail=f"Unsupported converter: {converter}"
        )
    return html_to_blocks(html)


class VoltoBody(BaseModel):
    """
    Request body model for HTML to Volto blocks conversion with layout.

    Attributes:
        html (str): The HTML content to convert.
        default_blocks (list[VoltoBlock] | None): Default blocks to include.
        additional_blocks (list[VoltoBlock] | None): Additional blocks to include.
    """

    html: str
    default_blocks: list[t.VoltoBlock] | None = None
    additional_blocks: list[t.VoltoBlock] | None = None


@router.post("/volto")
def convert_to_volto(body: VoltoBody) -> t.VoltoBlocksInfo:
    """
    Convert HTML to Volto blocks and return blocks information.

    Converts the provided HTML content to a Volto blocks structure, including
    block layout.

    Args:
        body (VoltoBody): Request body containing HTML and block lists.

    Returns:
        VoltoBlocksInfo: Information about the converted Volto blocks and layout.

    Example::

        $ curl -X POST /volto -d '{"html": "<p>Hello</p>"}'
    """
    html = body.html
    default_blocks = body.default_blocks or []
    additional_blocks = body.additional_blocks or []
    return volto_blocks(html, default_blocks, additional_blocks)

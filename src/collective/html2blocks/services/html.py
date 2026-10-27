"""
HTML and Markdown conversion service for ``collective.html2blocks``.

Provides API endpoints for converting HTML or Markdown content to Volto blocks and
block layout information. Includes endpoints for both simple block conversion and
full Volto layout.

Example:
    .. code-block:: console

        POST /html
        POST /markdown
        POST /volto
"""

from collective.html2blocks import _types as t
from collective.html2blocks.converter import html_to_blocks
from collective.html2blocks.converter import markdown_to_blocks
from collective.html2blocks.converter import volto_blocks
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Literal


router = APIRouter()


class HtmlBody(BaseModel):
    """
    Request body model for HTML to blocks conversion.

    Attributes:
        html (str): The HTML content to convert.
        converter (str): The type of conversion to perform (default is ``slate``).
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

    Example:
        .. code-block:: shell

            curl -X POST /html -d '{"html": "<p>Hello</p>", "converter": "slate"}'
    """
    converter = body.converter
    html = body.html
    if converter not in ["slate"]:
        raise HTTPException(
            status_code=400, detail=f"Unsupported converter: {converter}"
        )
    return html_to_blocks(html)


class MarkdownBody(BaseModel):
    """
    Request body model for Markdown to blocks conversion.

    :ivar markdown: The Markdown content to convert.
    :ivar converter: The type of conversion to perform (default is ``slate``).
    """

    markdown: str
    converter: str = "slate"


@router.post("/markdown")
async def convert_markdown(body: MarkdownBody) -> list[t.VoltoBlock]:
    """
    Convert Markdown to blocks.

    Converts the provided Markdown content to a list of Volto blocks using the
    specified converter.

    :param body: Request body containing Markdown and converter type.
    :returns: The converted blocks.
    :raises HTTPException: If an unsupported converter is specified.

    Example:
        .. code-block:: shell

            curl -X POST /markdown -d '{"markdown": "# Hello", "converter": "slate"}'
    """
    converter = body.converter
    markdown = body.markdown
    if converter not in ["slate"]:
        raise HTTPException(
            status_code=400, detail=f"Unsupported converter: {converter}"
        )
    return markdown_to_blocks(markdown)


class VoltoBody(BaseModel):
    """
    Request body model for HTML or Markdown to Volto blocks conversion with layout.

    :ivar html: The HTML or Markdown content to convert.
    :ivar format: The format of ``html``, either ``html`` (default) or ``markdown``.
    :ivar default_blocks: Default blocks to include.
    :ivar additional_blocks: Additional blocks to include.
    """

    html: str
    format: Literal["html", "markdown"] = "html"
    default_blocks: list[t.VoltoBlock] | None = None
    additional_blocks: list[t.VoltoBlock] | None = None


@router.post("/volto")
def convert_to_volto(body: VoltoBody) -> t.VoltoBlocksInfo:
    """
    Convert HTML or Markdown to Volto blocks and return blocks information.

    Converts the provided content to a Volto blocks structure, including block
    layout. The ``format`` field tells whether the content is HTML or Markdown.

    :param body: Request body containing the content, its format and block lists.
    :returns: Information about the converted Volto blocks and layout.

    Example:
        .. code-block:: shell

            curl -X POST /volto -d '{"html": "<p>Hello</p>"}'
            curl -X POST /volto -d '{"html": "# Hello", "format": "markdown"}'
    """
    html = body.html
    default_blocks = body.default_blocks or []
    additional_blocks = body.additional_blocks or []
    return volto_blocks(
        html, default_blocks, additional_blocks, source_format=body.format
    )

"""
HTML and Markdown conversion service for ``collective.html2blocks``.

Provides API endpoints for converting HTML or Markdown content to Volto blocks and
block layout information. Includes endpoints for both simple block conversion and
full Volto layout.

The endpoints use the ``slate`` converter unless ``converter`` is ``plate``, which
produces the Plate value of Plone Aurora. ``POST /slate2plate`` adds that value to an
existing content item. ``plate_format`` picks where it goes: ``main`` (default) for
``blocks["main"]``, or ``somersault`` for the ``__somersault__`` block of Aurora sites
that have not upgraded yet. It is a body field of ``/html``, ``/markdown`` and
``/volto``, and a query parameter of ``/slate2plate``, whose body is the content item.

Example:
    .. code-block:: console

        POST /html
        POST /markdown
        POST /volto
        POST /slate2plate
"""

from collective.html2blocks import _types as t
from collective.html2blocks.converter import ConverterName
from collective.html2blocks.converter import PlateFormat
from collective.html2blocks.converter import html_to_blocks
from collective.html2blocks.converter import markdown_to_blocks
from collective.html2blocks.converter import slate_to_plate
from collective.html2blocks.converter import volto_blocks
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Any
from typing import Literal
from typing import cast


router = APIRouter()

# The ``blocks`` setting of a request, see
# :func:`~collective.html2blocks.registry.resolve_blocks`.
BlocksField = dict[str, bool | dict[str, Any]] | None


def _bad_request(exc: ValueError) -> HTTPException:
    """Return the 400 response for an invalid ``blocks`` setting."""
    return HTTPException(status_code=400, detail=str(exc))


class HtmlBody(BaseModel):
    """
    Request body model for HTML to blocks conversion.

    Attributes:
        html (str): The HTML content to convert.
        converter (str): The type of conversion to perform, ``slate`` (default) or
            ``plate``.
        title (str): The title of the content, for the ``plate`` converter.
        blocks (dict, optional): Enables, disables and configures block types.
        plate_format (str): For the ``plate`` converter, ``main`` (default) or
            ``somersault``.
    """

    html: str
    converter: str = "slate"
    title: str = ""
    blocks: BlocksField = None
    plate_format: str = "main"


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
        HTTPException: If an unsupported converter or Plate format is specified.

    Example:
        .. code-block:: shell

            curl -X POST /html -d '{"html": "<p>Hello</p>", "converter": "slate"}'
    """
    converter = cast(ConverterName, body.converter)
    try:
        return html_to_blocks(
            body.html,
            blocks=body.blocks,
            converter=converter,
            title=body.title,
            plate_format=cast(PlateFormat, body.plate_format),
        )
    except ValueError as exc:
        raise _bad_request(exc) from None


class MarkdownBody(BaseModel):
    """
    Request body model for Markdown to blocks conversion.

    :ivar markdown: The Markdown content to convert.
    :ivar converter: The type of conversion to perform, ``slate`` (default) or
        ``plate``.
    :ivar title: The title of the content, for the ``plate`` converter.
    :ivar blocks: Enables, disables and configures block types.
    :ivar plate_format: For the ``plate`` converter, ``main`` (default) or
        ``somersault``.
    """

    markdown: str
    converter: str = "slate"
    title: str = ""
    blocks: BlocksField = None
    plate_format: str = "main"


@router.post("/markdown")
async def convert_markdown(body: MarkdownBody) -> list[t.VoltoBlock]:
    """
    Convert Markdown to blocks.

    Converts the provided Markdown content to a list of Volto blocks using the
    specified converter.

    :param body: Request body containing Markdown and converter type.
    :returns: The converted blocks.
    :raises HTTPException: If an unsupported converter or Plate format is specified.

    Example:
        .. code-block:: shell

            curl -X POST /markdown -d '{"markdown": "# Hello", "converter": "slate"}'
    """
    converter = cast(ConverterName, body.converter)
    try:
        return markdown_to_blocks(
            body.markdown,
            blocks=body.blocks,
            converter=converter,
            title=body.title,
            plate_format=cast(PlateFormat, body.plate_format),
        )
    except ValueError as exc:
        raise _bad_request(exc) from None


class VoltoBody(BaseModel):
    """
    Request body model for HTML or Markdown to Volto blocks conversion with layout.

    :ivar html: The HTML or Markdown content to convert.
    :ivar format: The format of ``html``, either ``html`` (default) or ``markdown``.
    :ivar default_blocks: Default blocks to include.
    :ivar additional_blocks: Additional blocks to include.
    :ivar blocks: Enables, disables and configures block types, keyed by
        their Volto ``@type``: ``true`` or an object of options enables a
        block, ``false`` disables it.
    :ivar converter: The type of conversion to perform, ``slate`` (default) or
        ``plate``.
    :ivar title: The title of the content, for a ``title`` block with the ``plate``
        converter.
    :ivar plate_format: For the ``plate`` converter, ``main`` (default) for
        ``blocks["main"]``, or ``somersault`` for ``blocks["__somersault__"]``.
    """

    html: str
    format: Literal["html", "markdown"] = "html"
    default_blocks: list[t.VoltoBlock] | None = None
    additional_blocks: list[t.VoltoBlock] | None = None
    blocks: BlocksField = None
    converter: str = "slate"
    title: str = ""
    plate_format: str = "main"


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
            curl -X POST /volto -d '{"html": "<pre>ls</pre>",
                                     "blocks": {"codeBlock": true}}'
            curl -X POST /volto -d '{"html": "<p>Hello</p>", "converter": "plate"}'
    """
    html = body.html
    default_blocks = body.default_blocks or []
    additional_blocks = body.additional_blocks or []
    try:
        return volto_blocks(
            html,
            default_blocks,
            additional_blocks,
            source_format=body.format,
            blocks=body.blocks,
            converter=cast(ConverterName, body.converter),
            title=body.title,
            plate_format=cast(PlateFormat, body.plate_format),
        )
    except ValueError as exc:
        raise _bad_request(exc) from None


class ContentBody(BaseModel):
    """
    Request body model for Slate to Plate conversion of a content item.

    The other keys of the content item are returned unchanged.

    :ivar blocks: The blocks of the content item.
    :ivar blocks_layout: The layout of the blocks.
    :ivar title: The title of the content item, for a ``title`` block.
    """

    model_config = ConfigDict(extra="allow")

    blocks: dict[str, dict[str, Any]]
    blocks_layout: dict[str, Any]
    title: str = ""


@router.post("/slate2plate")
def convert_slate_to_plate(
    body: ContentBody, plate_format: str = "main"
) -> dict[str, Any]:
    """
    Add the Plate value of Plone Aurora to a content item with Slate blocks.

    The existing blocks stay, and a content item that already has a ``main`` or a
    ``__somersault__`` block comes back unchanged.

    :param body: The content item.
    :param plate_format: Query parameter, ``main`` (default) for
        ``blocks["main"]``, or ``somersault`` for ``blocks["__somersault__"]``.
    :returns: The content item with the block of the Plate value.
    :raises HTTPException: If an unsupported Plate format is specified.

    Example:
        .. code-block:: shell

            curl -X POST /slate2plate -d '{"title": "Welcome",
                                           "blocks": {"a": {"@type": "title"}},
                                           "blocks_layout": {"items": ["a"]}}'
            curl -X POST '/slate2plate?plate_format=somersault' -d '{...}'
    """
    try:
        return slate_to_plate(
            body.model_dump(), plate_format=cast(PlateFormat, plate_format)
        )
    except ValueError as exc:
        raise _bad_request(exc) from None

from collective.html2blocks import _types as t
from collective.html2blocks.converter import html_to_blocks
from collective.html2blocks.converter import volto_blocks
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel


router = APIRouter()


class HtmlBody(BaseModel):
    html: str
    converter: str = "slate"


@router.post("/html")
async def convert_html(body: HtmlBody) -> list[t.VoltoBlock]:
    """Convert HTML to blocks.

    Args:
        html (str): The HTML content to convert.
        converter (str): The type of conversion to perform (default is "slate").

    Returns:
        list: A list containing the converted blocks.
    """
    converter = body.converter
    html = body.html
    if converter not in ["slate"]:
        raise HTTPException(
            status_code=400, detail=f"Unsupported converter: {converter}"
        )
    return html_to_blocks(html)


class VoltoBody(BaseModel):
    html: str
    default_blocks: list[t.VoltoBlock] | None = None
    additional_blocks: list[t.VoltoBlock] | None = None


@router.post("/volto")
def convert_to_volto(body: VoltoBody) -> t.VoltoBlocksInfo:
    """Convert HTML to Volto blocks and return blocks information.

    Args:
        html (str): The HTML content to convert.
        default_blocks (list, optional): Default blocks to include in the conversion.
        additional_blocks (list, optional): Additional blocks to be included
                                            in the conversion.

    Returns:
        VoltoBlocksInfo: Information about the converted Volto blocks.
    """
    html = body.html
    default_blocks = body.default_blocks or []
    additional_blocks = body.additional_blocks or []
    return volto_blocks(html, default_blocks, additional_blocks)

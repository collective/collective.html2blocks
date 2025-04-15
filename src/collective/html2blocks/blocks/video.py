from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.blocks.iframe import youtube



@registry.block_converter("video")
def video_block(element: Element) -> list[VoltoBlock]:
    """Video block."""
    if not (src := element.get("src", "")):
        source: Element | None = element.source
        src = source.get("src", "")
    if youtube.get_youtube_video_id(src):
        return youtube._youtube_block(src)
    block = {"@type": "video", "url": src}
    return [block]

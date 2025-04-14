from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.utils.embed import YOUTUBE_REGEX

import re


def _get_youtube_video_id(url: str) -> str:
    video_id = ""
    if match := re.match(YOUTUBE_REGEX, url):
        video_id = match.group("provider_id")
    return video_id


@registry.block_converter("video")
def video_block(element: Element) -> list[VoltoBlock]:
    """Video block."""
    if not (src := element.get("src", "")):
        source: Element | None = element.source
        src = source.get("src", "")
    youtube_id = _get_youtube_video_id(src)
    url = f"https://youtu.be/{youtube_id}" if youtube_id else src
    block = {"@type": "video", "url": url}
    return [block]

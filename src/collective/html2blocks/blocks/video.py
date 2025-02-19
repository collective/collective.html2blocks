from collective.html2blocks import registry
from collective.html2blocks._types import Element

import re


def _get_youtube_video_id(url: str) -> str:
    video_id = ""
    pattern = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(?:-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)(?P<video_id>[\w\-]+)(\S+)?$"  # noQA: E501
    if match := re.match(pattern, url):
        video_id = match.group("video_id")
    return video_id


@registry.block_converter("video")
def video_block(element: Element) -> list[dict]:
    """Video block."""
    if not (src := element.get("src", "")):
        source: Element | None = element.source
        src = source.get("src", "")
    youtube_id = _get_youtube_video_id(src)
    url = f"https://youtu.be/{youtube_id}" if youtube_id else src
    block = {"@type": "video", "url": url}
    return [block]

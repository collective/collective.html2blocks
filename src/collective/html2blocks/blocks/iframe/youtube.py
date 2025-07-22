from collective.html2blocks import _types as t
from collective.html2blocks import registry

import re


YOUTUBE_REGEX = re.compile(
    r"^(http:|https:|)\/\/(m.|www.)?(youtu(be\.com|\.be|be\.googleapis\.com|be-nocookie\.com))\/(embed\/|watch\?v=|v\/)?(?P<provider_id>[A-Za-z0-9._%-]*)(\?\S+|\&\S+)?$"
)


def get_youtube_video_id(url: str) -> str:
    video_id = ""
    if match := re.match(YOUTUBE_REGEX, url):
        video_id = match.group("provider_id")
    return video_id


def _youtube_block(src: str) -> list[t.VoltoBlock]:
    """Return a block to display youtube videos."""
    block: t.VoltoBlock = {"@type": "video", "url": src}
    return [block]


@registry.iframe_converter(
    "youtube",
    src_pattern=YOUTUBE_REGEX,
    url_pattern=r"https://youtu.be/\g<provider_id>",
)
def youtube_block(element: t.Tag, src: str, provider_id: str) -> list[t.VoltoBlock]:
    """Implemented by @plone/volto."""
    return _youtube_block(src)

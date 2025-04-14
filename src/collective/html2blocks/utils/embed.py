from collective.html2blocks import _types as t
from urllib import parse

import re


YOUTUBE_REGEX = re.compile(
    r"^(http:|https:|)\/\/(m.|www.)?(youtu(be\.com|\.be|be\.googleapis\.com|be-nocookie\.com))\/(embed\/|watch\?v=|v\/)?(?P<provider_id>[A-Za-z0-9._%-]*)(\?\S+|\&\S+)?$"
)


PATTERNS = (
    (
        YOUTUBE_REGEX,
        r"https://youtu.be/\g<provider_id>",
        "youtube",
    ),
    (
        re.compile(
            r"https://w\.soundcloud.com/player/\?url=https%3A//api.soundcloud.com/tracks/(?P<provider_id>\d+)(.*)$"
        ),
        r"https://api.soundcloud.com/tracks/\g<provider_id>\2",
        "soundcloud",
    ),
    (
        re.compile(
            r"https://w\.soundcloud.com/player/\?url=https://api.soundcloud.com/tracks/(?P<provider_id>\d+)(.*)$"
        ),
        r"https://api.soundcloud.com/tracks/\g<provider_id>\2",
        "soundcloud",
    ),
)


def parse_embed_url(src: str) -> t.EmbedInfo:
    """Parse the url of an embeded content."""
    for pattern, repl, provider in PATTERNS:
        if match := re.match(pattern, src):
            raw_url = re.sub(pattern, repl, src).replace("&amp;", "&")
            provider_id = match.groupdict()["provider_id"]
            parsed = parse.urlparse(raw_url)
            return t.EmbedInfo(parsed.geturl(), provider_id, provider)
    return t.EmbedInfo(src, "", "other")

from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock

import re


SOUNDCLOUD_REGEX = re.compile(
    r"https://w\.soundcloud.com/player/\?url=https(%3A|:)//api.soundcloud.com/tracks/(?P<provider_id>\d+)(.*)$"
)


@registry.iframe_converter(
    "soundcloud",
    src_pattern=SOUNDCLOUD_REGEX,
    url_pattern=r"https://api.soundcloud.com/tracks/\g<provider_id>\2",
)
def soundcloud_block(element: Element, src: str, provider_id: str) -> list[VoltoBlock]:
    """Implemented by @kitconcept/volto-social-blocks."""
    block = {
        "@type": "soundcloudBlock",
        "soundcloudId": provider_id,
        "align": "center",
        "size": "l",
    }
    return [block]

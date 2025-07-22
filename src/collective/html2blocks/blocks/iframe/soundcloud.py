from collective.html2blocks import _types as t
from collective.html2blocks import registry

import re


SOUNDCLOUD_REGEX = re.compile(
    r"https://w\.soundcloud.com/player/\?url=https(%3A|:)//api.soundcloud.com/tracks/(?P<provider_id>\d+)(.*)$"
)


@registry.iframe_converter(
    "soundcloud",
    src_pattern=SOUNDCLOUD_REGEX,
    url_pattern=r"https://api.soundcloud.com/tracks/\g<provider_id>\2",
)
def soundcloud_block(element: t.Tag, src: str, provider_id: str) -> list[t.VoltoBlock]:
    """Implemented by @kitconcept/volto-social-blocks."""
    block: t.VoltoBlock = {
        "@type": "soundcloudBlock",
        "soundcloudId": provider_id,
        "align": "center",
        "size": "l",
    }
    return [block]

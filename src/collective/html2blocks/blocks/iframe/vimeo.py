from collective.html2blocks import _types as t
from collective.html2blocks import registry

import re


VIMEO_REGEX = re.compile(
    r"^(https?:)?//(www\.|player\.)?vimeo\.com/(video/)?(?P<provider_id>\d+)([/?#]\S*)?$"
)


@registry.iframe_converter(
    "vimeo",
    src_pattern=VIMEO_REGEX,
    url_pattern=r"https://vimeo.com/\g<provider_id>",
    block_type="video",
    package="@plone/volto",
)
def vimeo_block(element: t.Tag, src: str, provider_id: str) -> list[t.VoltoBlock]:
    """
    Implemented by @plone/volto.

    The video block reads the Vimeo id from what follows ``.com/``, so the URL
    is always ``https://vimeo.com/<id>``, never the player URL.
    """
    block: t.VoltoBlock = {"@type": "video", "url": src}
    return [block]

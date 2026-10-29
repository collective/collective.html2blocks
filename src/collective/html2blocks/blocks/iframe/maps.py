from collective.html2blocks import _types as t
from collective.html2blocks import registry

import re


GOOGLE_MAPS_REGEX = re.compile(
    r"^(https?:)?//(www\.|maps\.)?google\.com/maps(/embed)?(?P<provider_id>[?/].*)$"
)


@registry.iframe_converter(
    "googlemaps",
    src_pattern=GOOGLE_MAPS_REGEX,
    url_pattern=r"\g<0>",
    block_type="maps",
    package="@plone/volto",
    description="Maps: Google Maps <iframe>.",
)
def google_maps_block(element: t.Tag, src: str, provider_id: str) -> list[t.VoltoBlock]:
    """Implemented by @plone/volto, which embeds the ``url`` of the block."""
    block: t.VoltoBlock = {"@type": "maps", "url": src}
    if title := element.get("title"):
        block["title"] = str(title)
    return [block]

from .soundcloud import soundcloud_block
from .youtube import youtube_block
from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.utils.markup import url_from_iframe


__all__ = [
    "iframe_block",
    "iframe_default_block",
    "soundcloud_block",
    "youtube_block",
]


@registry.iframe_converter("iframe")
def iframe_default_block(
    element: Element, src: str, provider_id: str
) -> list[VoltoBlock]:
    """Implemented by @kitconcept/volto-iframe-block."""
    height = element.get("height", "200px")
    block = {"@type": "iframe", "src": src, "width": "full", "height": height}
    return [block]


@registry.block_converter("iframe")
def iframe_block(element: Element) -> list[VoltoBlock]:
    """Variations of the iframe block."""
    src = url_from_iframe(element)
    embed_info = registry.get_iframe_converter(src)
    return embed_info.converter(element, embed_info.url, embed_info.provider_id)

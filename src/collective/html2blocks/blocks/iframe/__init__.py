from .soundcloud import soundcloud_block
from .youtube import youtube_block
from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.utils.markup import url_from_iframe


__all__ = [
    "iframe_block",
    "iframe_default_block",
    "soundcloud_block",
    "youtube_block",
]


@registry.iframe_converter("iframe")
def iframe_default_block(
    element: t.Tag, src: str, provider_id: str
) -> Generator[t.VoltoBlock, None, None]:
    """Implemented by @kitconcept/volto-iframe-block."""
    height = element.get("height", "200px")
    yield {"@type": "iframe", "src": src, "width": "full", "height": height}


@registry.block_converter("iframe")
def iframe_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """Variations of the iframe block."""
    src = url_from_iframe(element)
    embed_info = registry.get_iframe_converter(src)
    yield from embed_info.converter(element, embed_info.url, embed_info.provider_id)

from bs4 import BeautifulSoup
from collective.html2blocks import registry
from collective.html2blocks._types import Element
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks.utils.embed import parse_embed_url
from collective.html2blocks.utils.markup import url_from_iframe


def _iframe(element: Element, src: str, provider_id: str) -> list[VoltoBlock]:
    """Implemented by @kitconcept/volto-iframe-block."""
    height = element.get("height", "200px")
    block = {"@type": "iframe", "src": src, "width": "full", "height": height}
    return [block]


def _youtube(element: Element, src: str, provider_id: str) -> list[VoltoBlock]:
    """Implemented by @plone/volto."""
    block = {"@type": "video", "url": src}
    return [block]


def _soundcloud(element: Element, src: str, provider_id: str) -> list[VoltoBlock]:
    """Implemented by @kitconcept/volto-social-blocks."""
    block = {
        "@type": "soundcloudBlock",
        "soundcloudId": provider_id,
        "align": "center",
        "size": "l",
    }
    return [block]


PROVIDERS = {
    "youtube": _youtube,
    "soundcloud": _soundcloud,
    "default": _iframe,
}


def blocks_from_iframe(source: str) -> list[VoltoBlock]:
    """Variations of the iframe block."""
    element = BeautifulSoup(source, features="html.parser")
    return iframe_block(element)


@registry.block_converter("iframe")
def iframe_block(element: Element) -> list[VoltoBlock]:
    """Variations of the iframe block."""
    src = url_from_iframe(element)
    embed = parse_embed_url(src)
    func = PROVIDERS.get(embed.provider, PROVIDERS["default"])
    return func(element, embed.url, embed.provider_id)

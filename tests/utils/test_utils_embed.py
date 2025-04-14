from collective.html2blocks._types import EmbedInfo
from collective.html2blocks.utils import embed as utils

import pytest


@pytest.mark.parametrize(
    "src,url,provider_id,provider",
    [
        (
            "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/1275507478&amp;color=%23ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false&amp;show_teaser=true&amp;visual=true",
            "https://api.soundcloud.com/tracks/1275507478&color=%23ff5500&auto_play=false&hide_related=false&show_comments=true&show_user=true&show_reposts=false&show_teaser=true&visual=true",
            "1275507478",
            "soundcloud",
        ),
        (
            "https://www.youtube.com/embed/44CE2XOFS98",
            "https://youtu.be/44CE2XOFS98",
            "44CE2XOFS98",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/45r8eU5McWY?feature=oembed",
            "https://youtu.be/45r8eU5McWY",
            "45r8eU5McWY",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/47kARG37pUs?feature=oembed",
            "https://youtu.be/47kARG37pUs",
            "47kARG37pUs",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/49wYuZR1RpI?feature=oembed",
            "https://youtu.be/49wYuZR1RpI",
            "49wYuZR1RpI",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/4OUAlDfN2p0?feature=oembed",
            "https://youtu.be/4OUAlDfN2p0",
            "4OUAlDfN2p0",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/4SIY72714lw?feature=oembed",
            "https://youtu.be/4SIY72714lw",
            "4SIY72714lw",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/4hJAxcKbv6Y?feature=oembed",
            "https://youtu.be/4hJAxcKbv6Y",
            "4hJAxcKbv6Y",
            "youtube",
        ),
        (
            "https://www.youtube.com/embed/4ifeX38vKGU?feature=oembed",
            "https://youtu.be/4ifeX38vKGU",
            "4ifeX38vKGU",
            "youtube",
        ),
        (
            "https://anchor.fm/oassuntoe/embed/episodes/O-Assunto----Agrotxicos-enm3en",
            "https://anchor.fm/oassuntoe/embed/episodes/O-Assunto----Agrotxicos-enm3en",
            "",
            "other",
        ),
    ],
)
def test_parse_embed_url(src: str, url: str, provider_id: str, provider: str):
    func = utils.parse_embed_url
    result = func(src)
    assert isinstance(result, EmbedInfo)
    assert result.url == url
    assert result.provider_id == provider_id
    assert result.provider == provider

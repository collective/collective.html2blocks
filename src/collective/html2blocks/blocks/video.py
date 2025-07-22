from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.blocks.iframe import youtube


@registry.block_converter("video")
def video_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """Video block."""
    if not (src := element.get("src", "")):
        source: t.Tag | None = element.source
        src = str(source.get("src", "")) if source else ""
    if youtube.get_youtube_video_id(src):
        yield from youtube._youtube_block(src)
    yield {"@type": "video", "url": src}

"""
Video block converter for collective.html2blocks.

This module provides the block converter for <video> elements, transforming them
into Volto video blocks. It supports YouTube video detection and delegates to the
iframe converter for YouTube URLs, otherwise yielding a standard video block.

Implementation details:
- Extracts video src from the element or its source child.
- Detects YouTube videos and uses the YouTube block converter if applicable.
- Yields a Volto video block with the video URL.

Example usage::

    from collective.html2blocks.blocks.video import video_block
    blocks = list(video_block(element))
"""

from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.blocks.iframe import youtube


@registry.block_converter("video")
def video_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """
    Convert a <video> element to a Volto video block.

    This converter extracts the video src, detects YouTube videos, and yields a
    Volto video block. If the video is a YouTube URL, it delegates to the YouTube
    block converter for proper handling.

    Args:
        element (Tag): The <video> element to convert.

    Yields:
        VoltoBlock: The converted video block.

    Example::

        blocks = list(video_block(element))
        # [{'@type': 'video', 'url': ...}]
    """
    if not (src := element.get("src", "")):
        source: t.Tag | None = element.source
        src = str(source.get("src", "")) if source else ""
    if youtube.get_youtube_video_id(src):
        yield from youtube._youtube_block(src)
    yield {"@type": "video", "url": src}

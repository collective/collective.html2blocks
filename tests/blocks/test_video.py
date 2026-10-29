from collective.html2blocks.blocks import iframe
from collective.html2blocks.blocks import video

import pytest


VIDEO_INTERNAL = '<video src="/video/pass-countdown.ogg" width="170" height="85" controls><p>If you are reading this, it is because your browser does not support the HTML5 video element.</p></video>'
VIDEO_EXTERNAL = '<video src="https://plone.org/video.mp4" width="170" height="85" />'
VIDEO_YOUTUBE = '<video src="https://youtu.be/jn4zGVJq9m0" width="170" height="85" />'
VIDEO_YOUTUBE_SOURCE = (
    '<video width="170" height="85"><source src="https://youtu.be/47BC9R2vD2w"></video>'
)


@pytest.mark.parametrize(
    "source,key,expected",
    [
        [VIDEO_INTERNAL, "@type", "video"],
        [VIDEO_INTERNAL, "url", "/video/pass-countdown.ogg"],
        [VIDEO_EXTERNAL, "@type", "video"],
        [VIDEO_EXTERNAL, "url", "https://plone.org/video.mp4"],
        [VIDEO_YOUTUBE, "@type", "video"],
        [VIDEO_YOUTUBE, "url", "https://youtu.be/jn4zGVJq9m0"],
        [VIDEO_YOUTUBE_SOURCE, "@type", "video"],
        [VIDEO_YOUTUBE_SOURCE, "url", "https://youtu.be/47BC9R2vD2w"],
    ],
)
def test_video_block(tag_from_str, source: str, key: str, expected: str):
    func = video.video_block
    element = tag_from_str(source)
    results = list(func(element))
    assert isinstance(results, list)
    result = results[0]
    assert isinstance(result, dict)
    assert result[key] == expected


@pytest.mark.parametrize(
    "source",
    [VIDEO_INTERNAL, VIDEO_EXTERNAL, VIDEO_YOUTUBE, VIDEO_YOUTUBE_SOURCE],
)
def test_video_block_yields_one_block(tag_from_str, source: str):
    results = list(video.video_block(tag_from_str(source)))
    assert len(results) == 1


@pytest.mark.parametrize(
    "src",
    [
        "https://www.youtube.com/watch?v=jn4zGVJq9m0",
        "https://youtube.com/embed/jn4zGVJq9m0?feature=oembed",
        "https://youtu.be/jn4zGVJq9m0",
    ],
)
def test_video_block_youtube_url_matches_iframe(tag_from_str, src: str):
    """A YouTube <video> gets the same URL as a YouTube <iframe>."""
    video_url = next(video.video_block(tag_from_str(f'<video src="{src}"></video>')))
    iframe_url = next(iframe.iframe_block(tag_from_str(f'<iframe src="{src}">')))
    assert video_url["url"] == "https://youtu.be/jn4zGVJq9m0"
    assert video_url == iframe_url

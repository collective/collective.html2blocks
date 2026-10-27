"""
Markdown utilities for ``collective.html2blocks``.

This module renders Markdown source to HTML, so that Markdown content can go
through the same HTML pipeline as any other input. Rendering follows CommonMark,
with tables and strikethrough enabled.

Example:
    .. code-block:: python

        from collective.html2blocks.utils import markdown
        html = markdown.markdown_to_html("# Title")
"""

from markdown_it import MarkdownIt


_PARSER = MarkdownIt("commonmark").enable(["table", "strikethrough"])


def markdown_to_html(source: str) -> str:
    """
    Render Markdown source as HTML.

    Args:
        source (str): The Markdown content to render.

    Returns:
        str: The HTML rendered from the Markdown source.

    Example:
        >>> markdown_to_html("**bold**")
        '<p><strong>bold</strong></p>\\n'
    """
    return _PARSER.render(source)

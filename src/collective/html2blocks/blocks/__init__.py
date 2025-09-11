"""
Block converters for collective.html2blocks.

This module imports and exposes the main block converter functions for HTML elements
such as iframe, image, slate (rich text), table, and video. These converters are
registered with the html2blocks registry and are used to transform HTML elements
into Volto blocks for use in Plone/Volto content management systems.

Each converter implements a specific strategy for handling its corresponding HTML tag:

- `iframe_block`: Converts <iframe> elements to Volto embed blocks,
  handling provider-specific logic.
- `image_block`: Converts <img> elements to Volto image blocks,
  extracting src, alt, and other attributes.
- `slate_block`: Converts rich text elements (paragraphs, headings,
  lists, etc.) to Volto Slate blocks, supporting nested and inline content.
- `table_block`: Converts <table> elements to Volto table blocks,
  handling headers, rows, and cell types.
- `video_block`: Converts <video> elements to Volto video blocks,
  extracting sources and metadata.

These converters are registered using decorators and can be extended or referenced
by other developers to implement custom block conversion logic. See the implementation
of each block in its respective module for details on parsing, normalization, and
Volto block structure.

Example usage::

    from collective.html2blocks.blocks import slate_block
    blocks = slate_block(element)

For custom converters, use the registry decorators:

    from collective.html2blocks.registry import block_converter

    @block_converter('custom')
    def custom_block(element):
        ...

__all__ lists the available block converters for import and reference.
"""

from .iframe import iframe_block
from .image import image_block
from .slate import slate_block
from .table import table_block
from .video import video_block


__all__ = [
    "iframe_block",
    "image_block",
    "slate_block",
    "table_block",
    "video_block",
]

"""
Constants for inline and empty HTML elements in collective.html2blocks.

This module defines tuples of tag names that are considered inline elements
or allowed to be empty when converting HTML to Volto blocks.

Example usage::

    from collective.html2blocks.utils.inline import ALLOW_EMPTY_ELEMENTS
    from collective.html2blocks.utils.inline import INLINE_ELEMENTS

    if tag in INLINE_ELEMENTS:
        ...
    if tag in ALLOW_EMPTY_ELEMENTS:
        ...
"""

INLINE_ELEMENTS = (
    "b",
    "br",
    "code",
    "em",
    "i",
    "link",
    "s",
    "strong",
    "sub",
    "sup",
    "u",
)
"""
Tuple of tag names considered inline elements.

These elements are treated as inline when converting HTML to Volto blocks.

Example::

    if tag in INLINE_ELEMENTS:
        ...
"""

ALLOW_EMPTY_ELEMENTS = ("br", "hr")
"""
Tuple of tag names allowed to be empty elements.

These elements are permitted to have no content when converting HTML.

Example::

    if tag in ALLOW_EMPTY_ELEMENTS:
        ...
"""

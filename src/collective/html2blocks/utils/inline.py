"""
Constants for inline and empty HTML elements in ``collective.html2blocks``.

This module defines tuples of tag names that are considered inline elements
or allowed to be empty when converting HTML to Volto blocks.

Example:
    .. code-block:: python

        from collective.html2blocks.utils.inline import ALLOW_EMPTY_ELEMENTS
        from collective.html2blocks.utils.inline import INLINE_ELEMENTS

        if tag in INLINE_ELEMENTS:
            # do something...
        if tag in ALLOW_EMPTY_ELEMENTS:
            # do something...
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

Example:
    .. code-block:: python

        if tag in INLINE_ELEMENTS:
            # do something...
"""

ALLOW_EMPTY_ELEMENTS = ("br", "hr")
"""
Tuple of tag names allowed to be empty elements.

These elements are permitted to have no content when converting HTML.

Example:
    .. code-block:: python

        if tag in ALLOW_EMPTY_ELEMENTS:
            # do something...
"""

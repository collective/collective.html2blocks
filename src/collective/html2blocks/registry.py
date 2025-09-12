"""
Registry for block, element, and iframe converters in ``collective.html2blocks``.

This module provides decorators and accessors for registering and retrieving
converter functions that transform HTML elements into Volto blocks or Slate items.

Converters are registered using decorators and stored in a global registry.
This enables extensible and dynamic HTML-to-block conversion for Plone/Volto.

Example:
    .. code-block:: python

        from collective.html2blocks.registry import block_converter

        @block_converter('p')
        def convert_paragraph(element):

See also:
    -   :meth:`block_converter`
    -   :meth:`element_converter`
    -   :meth:`iframe_converter`
    -   :meth:`get_block_converter`
    -   :meth:`get_element_converter`
    -   :meth:`get_iframe_converter`
    -   :meth:`report_registrations`
"""

from . import _types as t
from .logger import logger
from .utils.markup import cleanse_url
from collections.abc import Callable
from functools import wraps
from typing import cast

import re


_REGISTRY = t.Registry({}, {}, {})


class block_converter:
    """
    Decorator to register a block converter function for one or more tag names.

    Args:
        *tag_names (str): One or more HTML tag names to register the converter for.

    Example:
        .. code-block:: python

            @block_converter('p', 'div')
            def convert_paragraph(element):
    """

    def __init__(self, *tag_names: str):
        self.tag_names = tag_names

    def __call__(self, func: t.BlockConverter):
        friendly_name = f"{func.__module__}.{func.__name__}"
        for tag_name in self.tag_names:
            logger.debug(f"Registering block converter {friendly_name} to {tag_name}")
            _REGISTRY.block_converters[tag_name] = func
        return func


class element_converter:
    """
    Decorator to register an element converter function for one or more tag names.

    Args:
        tag_names (list[str]): List of HTML tag names to register the converter for.
        type_name (str, optional): Type name to use for the converter. Defaults to `""`.

    Example:
        .. code-block:: python

            @element_converter(['span'], 'strong')
            def convert_span(element, type_name):
    """

    def __init__(self, tag_names: list[str], type_name: str = ""):
        self.tag_names = tag_names
        self.type_name = type_name

    def __call__(self, func: t.ElementConverterFunc) -> t.ElementConverter:
        @wraps(func)
        def _inner_(element: t.Tag) -> t.SlateItemGenerator:
            type_name = self.type_name or element.name
            return func(element, type_name)

        # Cast to ElementConverter for type safety
        inner = cast(t.ElementConverter, _inner_)
        inner.__orig_mod__ = func.__module__

        friendly_name = f"{inner.__module__}.{inner.__name__}"
        for tag_name in self.tag_names:
            logger.debug(f"Registering element converter {friendly_name} to {tag_name}")
            _REGISTRY.element_converters[tag_name] = inner

        return inner


class iframe_converter:
    """
    Decorator to register an iframe converter function for a provider and pattern.

    Args:
        provider (str): The provider name (e.g., "youtube").
        src_pattern (re.Pattern | str, optional): Regex pattern for matching src URLs.
        url_pattern (str, optional): Replacement pattern for URLs.

    Example:
        .. code-block:: python

            @iframe_converter("youtube", r"https://youtube.com/embed/(?P<provider_id>[^/]+)")
            def convert_youtube_iframe(element):
    """

    def __init__(
        self, provider: str, src_pattern: re.Pattern | str = "", url_pattern: str = ""
    ):
        self.provider = provider
        self.src_pattern = src_pattern
        self.url_pattern = url_pattern

    def __call__(self, func: Callable):
        friendly_name = f"{func.__module__}.{func.__name__}"
        pattern = self.src_pattern if self.src_pattern else "default"
        provider = self.provider
        logger.debug(f"Registering iframe converter {friendly_name} to {provider}")
        converter = t.IFrameConverter(
            url_pattern=self.url_pattern,
            provider=provider,
            converter=func,
        )
        _REGISTRY.iframe_converters[pattern] = converter
        return func


def default_converter(func: t.BlockConverter) -> t.BlockConverter:
    """
    Register the default block converter.

    Args:
        func (BlockConverter): The converter function to use as default.

    Returns:
        BlockConverter: The registered default converter.

    Example:
        .. code-block:: python

            @default_converter
            def convert_default(element):
    """
    _REGISTRY.default = func
    return func


def elements_with_block_converters() -> list[str]:
    """
    Return a list of tag names with registered block converters.

    Returns:
        list[str]: List of tag names.

    Example:
        .. code-block:: pycon

            >>> elements_with_block_converters()
            ['p', 'div', ...]
    """
    if not _REGISTRY:
        return []
    return list(_REGISTRY.block_converters.keys())


def get_block_converter(
    element: t.Tag | None = None, tag_name: str = "", strict: bool = True
) -> Callable | None:
    """
    Return a registered block converter for a given element or tag name.

    Args:
        element (Tag, optional): The HTML element to get the converter for.
        tag_name (str, optional): The tag name to get the converter for.
        strict (bool, optional): If ``True``, only return if registered.
                                 If ``False``, fallback to default.

    Returns:
        Callable | None: The registered converter function, or ``None`` if not found.

    Example:
        .. code-block:: pycon

            >>> get_block_converter(tag_name='p')
            <function convert_paragraph ...>
    """
    if not (element or tag_name):
        raise RuntimeError("Should provide an element or a tag_name")
    if not tag_name and element:
        tag_name = element.name
    converter = _REGISTRY.block_converters.get(tag_name)
    if not converter and not strict and _REGISTRY.default:
        converter = _REGISTRY.default
    return converter


def get_element_converter(
    element: t.Tag | None = None, tag_name: str = ""
) -> t.ElementConverter | None:
    """
    Return a registered element converter for a given element or tag name.

    Args:
        element (Tag, optional): The HTML element to get the converter for.
        tag_name (str, optional): The tag name to get the converter for.

    Returns:
        ElementConverter | None: The registered converter function,
                                 or ``None`` if not found.

    Example:
        .. code-block:: pycon

            >>> get_element_converter(tag_name='span')
            <function convert_span ...>
    """
    if not (element or tag_name):
        raise RuntimeError("Should provide an element or a tag_name")
    if not tag_name and element:
        tag_name = element.name
    if _REGISTRY:
        converter = _REGISTRY.element_converters.get(tag_name)
        return converter
    return None


def get_iframe_converter(src: str) -> t.EmbedInfo:
    """
    Return a registered iframe converter for a given ``src`` URL.

    Args:
        src (str): The iframe ``src`` URL to match against registered patterns.

    Returns:
        EmbedInfo: Information about the matched provider and converter.

    Example:
        .. code-block:: pycon

            >>> get_iframe_converter('https://youtube.com/embed/abc123')
            EmbedInfo(url='...', provider_id='abc123', converter=<function ...>)
    """
    converters = _REGISTRY.iframe_converters
    for pattern, provider in converters.items():
        if pattern == "default":
            continue
        if match := re.match(pattern, src):
            repl = provider.url_pattern
            src = cleanse_url(re.sub(pattern, repl, src))
            provider_id = match.groupdict()["provider_id"]
            return t.EmbedInfo(src, provider_id, provider.converter)
    default = converters["default"]
    return t.EmbedInfo(src, "", default.converter)


def report_registrations() -> t.ReportRegistrations:
    """
    Return information about current converter registrations.

    Returns:
        ReportRegistrations: Dictionary with block, element, and iframe registrations.

    Example:
        .. code-block:: pycon

            >>> report_registrations()
            {'block': {...}, 'element': {...}, 'iframe': {...}}
    """
    report: t.ReportRegistrations = {"block": {}, "element": {}, "iframe": {}}
    for tag_name, blk_converter in _REGISTRY.block_converters.items():
        friendly_name = f"{blk_converter.__module__}.{blk_converter.__name__}"
        report["block"][tag_name] = friendly_name
    if converter_ := _REGISTRY.default:
        converter_name = f"{converter_.__module__}.{converter_.__name__}"
    else:
        # If no default converter is registered, we still want to report it
        # so that the user knows they can register one.
        converter_name = "No default converter registered"
    report["block"]["*"] = converter_name
    for tag_name, el_converter in _REGISTRY.element_converters.items():
        friendly_name = f"{el_converter.__orig_mod__}.{el_converter.__name__}"
        report["element"][tag_name] = friendly_name
    for provider in _REGISTRY.iframe_converters.values():
        iframe_converter = provider.converter
        friendly_name = f"{iframe_converter.__module__}.{iframe_converter.__name__}"
        provider_name = provider.provider
        report["iframe"][provider_name] = friendly_name
    return report


__all__ = [
    "block_converter",
    "default_converter",
    "element_converter",
    "get_block_converter",
    "get_element_converter",
    "get_iframe_converter",
    "iframe_converter",
    "report_registrations",
]


def _initialize_registry() -> t.Registry:
    """
    Initialize the registry and import all block modules.

    Returns:
        Registry: The initialized registry instance.
    """
    from collective.html2blocks import blocks  # noqa: F401

    return _REGISTRY


_initialize_registry()  # Ensure the registry is initialized on import

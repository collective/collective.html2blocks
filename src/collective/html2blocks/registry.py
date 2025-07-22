from . import _types as t
from .logger import logger
from .utils.markup import cleanse_url
from collections.abc import Callable
from functools import wraps
from typing import cast

import re


_REGISTRY = t.Registry({}, {}, {})


class block_converter:
    """Register a block converter."""

    def __init__(self, *tag_names: str):
        self.tag_names = tag_names

    def __call__(self, func: t.BlockConverter):
        friendly_name = f"{func.__module__}.{func.__name__}"
        for tag_name in self.tag_names:
            logger.debug(f"Registering block converter {friendly_name} to {tag_name}")
            _REGISTRY.block_converters[tag_name] = func
        return func


class element_converter:
    """Register an element converter."""

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
    """Register an iframe converter."""

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
    """Register the default converter."""
    _REGISTRY.default = func
    return func


def elements_with_block_converters() -> list[str]:
    """Return a list of tag names with registered element converters."""
    if not _REGISTRY:
        return []
    return list(_REGISTRY.block_converters.keys())


def get_block_converter(
    element: t.Tag | None = None, tag_name: str = "", strict: bool = True
) -> Callable | None:
    """Return a registered converter for a given element or tag_name."""
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
    """Return a registered converter for a given element or tag_name."""
    if not (element or tag_name):
        raise RuntimeError("Should provide an element or a tag_name")
    if not tag_name and element:
        tag_name = element.name
    if _REGISTRY:
        converter = _REGISTRY.element_converters.get(tag_name)
        return converter
    return None


def get_iframe_converter(src: str) -> t.EmbedInfo:
    """Return a registered converter for a given element src."""
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
    """Return information about current registrations."""
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
]


def _initialize_registry() -> t.Registry:
    """Initialize the registry."""
    from collective.html2blocks import blocks  # noqa: F401

    return _REGISTRY


_initialize_registry()  # Ensure the registry is initialized on import

from . import _types as t
from .logger import logger
from .utils.markup import cleanse_url
from collections.abc import Callable

import re


_REGISTRY: t.Registry | None


class block_converter:
    """Register a block converter."""

    def __init__(self, *tag_names: str):
        self.tag_names = tag_names

    def __call__(self, func: Callable):
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

    def __call__(self, func: Callable):
        def inner(element: t.Element):
            type_name = self.type_name
            if type_name == "":
                type_name = element.name
            return func(element, type_name)

        inner.__orig_mod__ = func.__module__
        inner.__name__ = func.__name__
        friendly_name = f"{inner.__orig_mod__}.{inner.__name__}"
        for tag_name in self.tag_names:
            logger.debug(f"Registering element converter {friendly_name} to {tag_name}")
            _REGISTRY.element_converters[tag_name] = inner
        return inner


class iframe_converter:
    """Register an iframe converter."""

    def __init__(
        self, provider: str, src_pattern: re.Pattern | None = "", url_pattern: str = ""
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


def default_converter(func: Callable):
    """Register the default converter."""
    _REGISTRY.default = func
    return func


def elements_with_block_converters() -> list[str]:
    """Return a list of tag names with registered element converters."""
    if not _REGISTRY:
        return []
    return list(_REGISTRY.block_converters.keys())


def get_block_converter(
    element: t.Element | None = None, tag_name: str = "", strict: bool = True
) -> Callable | None:
    """Return a registered converter for a given element or tag_name."""
    if not (element or tag_name):
        raise RuntimeError("Should provide an element or a tag_name")
    tag_name = tag_name if tag_name else element.name
    converter = _REGISTRY.block_converters.get(tag_name)
    if not converter and not strict:
        converter = _REGISTRY.default
    return converter


def get_element_converter(
    element: t.Element | None = None, tag_name: str = ""
) -> Callable | None:
    """Return a registered converter for a given element or tag_name."""
    if not (element or tag_name):
        raise RuntimeError("Should provide an element or a tag_name")
    tag_name = tag_name if tag_name else element.name
    converter = _REGISTRY.element_converters.get(tag_name)
    return converter


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
    default = converters.get("default")
    return t.EmbedInfo(src, "", default.converter)


def report_registrations() -> dict[str, dict]:
    """Return information about current registrations."""
    report = {"block": {}, "element": {}, "iframe": {}}
    for tag_name, converter in _REGISTRY.block_converters.items():
        friendly_name = f"{converter.__module__}.{converter.__name__}"
        report["block"][tag_name] = friendly_name
    converter = _REGISTRY.default
    report["block"]["*"] = f"{converter.__module__}.{converter.__name__}"
    for tag_name, converter in _REGISTRY.element_converters.items():
        friendly_name = f"{converter.__orig_mod__}.{converter.__name__}"
        report["element"][tag_name] = friendly_name
    for provider in _REGISTRY.iframe_converters.values():
        converter = provider.converter
        friendly_name = f"{converter.__module__}.{converter.__name__}"
        report["iframe"][provider.provider] = friendly_name
    return report


def _initialize_registry() -> t.Registry:
    global _REGISTRY
    _REGISTRY = t.Registry({}, {}, {})
    from collective.html2blocks import blocks  # noQA: F401


_initialize_registry()

__all__ = [
    "block_converter",
    "default_converter",
    "element_converter",
    "get_block_converter",
    "get_element_converter",
    "get_iframe_converter",
    "iframe_converter",
]

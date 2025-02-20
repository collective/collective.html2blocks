from ._types import Element
from ._types import Registry
from .logger import logger
from collections.abc import Callable


_REGISTRY: Registry | None


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
        def inner(element: Element):
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


def default_converter(func: Callable):
    """Register the default converter."""
    _REGISTRY.default = func
    return func


def get_block_converter(
    element: Element | None = None, tag_name: str = "", strict: bool = True
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
    element: Element | None = None, tag_name: str = ""
) -> Callable | None:
    """Return a registered converter for a given element or tag_name."""
    if not (element or tag_name):
        raise RuntimeError("Should provide an element or a tag_name")
    tag_name = tag_name if tag_name else element.name
    converter = _REGISTRY.element_converters.get(tag_name)
    return converter


def report_registrations() -> dict[str, dict]:
    """Return information about current registrations."""
    report = {"block": {}, "element": {}}
    for tag_name, converter in _REGISTRY.block_converters.items():
        friendly_name = f"{converter.__module__}.{converter.__name__}"
        report["block"][tag_name] = friendly_name
    converter = _REGISTRY.default
    report["block"]["*"] = f"{converter.__module__}.{converter.__name__}"
    for tag_name, converter in _REGISTRY.element_converters.items():
        friendly_name = f"{converter.__orig_mod__}.{converter.__name__}"
        report["element"][tag_name] = friendly_name
    return report


def _initialize_registry() -> Registry:
    global _REGISTRY
    _REGISTRY = Registry({}, {})
    from collective.html2blocks import blocks  # noQA: F401


_initialize_registry()

__all__ = [
    "block_converter",
    "default_converter",
    "element_converter",
    "get_block_converter",
    "get_element_converter",
]

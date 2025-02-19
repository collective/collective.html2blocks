from ._types import Element
from ._types import Registry
from collections.abc import Callable


class block_converter:
    """Register a block converter."""

    def __init__(self, *tag_names):
        self.tag_names = tag_names

    def __call__(self, func: Callable):
        for tag_name in self.tag_names:
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
        for tag_name in self.tag_names:
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
        return RuntimeError("Should provide an element or a tag_name")
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
        return RuntimeError("Should provide an element or a tag_name")
    tag_name = tag_name if tag_name else element.name
    converter = _REGISTRY.element_converters.get(tag_name)
    return converter


def _registry_report():
    from collective.html2blocks import blocks  # noQA: F401

    block_converters = _REGISTRY.block_converters
    element_converters = _REGISTRY.element_converters
    print("Block Converters")
    for tag_name, converter in block_converters.items():
        print(f" - {tag_name}: {converter.__module__}.{converter.__name__}")
    print("Element Converters")
    for tag_name, converter in element_converters.items():
        print(f" - {tag_name}: {converter.__orig_mod__}.{converter.__name__}")


def _initialize_registry() -> Registry:
    return Registry({}, {})


_REGISTRY: Registry = _initialize_registry()

__all__ = [
    "block_converter",
    "default_converter",
    "element_converter",
    "get_block_converter",
    "get_element_converter",
]

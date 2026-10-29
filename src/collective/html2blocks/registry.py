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
from collections.abc import Generator
from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Any
from typing import cast
from typing import get_type_hints

import dataclasses
import re


_REGISTRY = t.Registry({}, {}, {})

# Tags whose block converters are hidden during a conversion, see
# :func:`hidden_block_converters`.
_HIDDEN_TAGS: ContextVar[frozenset[str]] = ContextVar(
    "hidden_block_tags", default=frozenset()
)

# The ``blocks`` setting of the conversion in progress, see :func:`conversion`.
# ``None`` means no conversion is active, and the defaults apply.
_BLOCKS: ContextVar[t.ResolvedBlocks | None] = ContextVar("blocks", default=None)

# Cache of the defaults, cleared whenever a block type changes.
_DEFAULT_BLOCKS: list[t.ResolvedBlocks] = []

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})


def _friendly_name(func: Callable) -> str:
    module = getattr(func, "__orig_mod__", func.__module__)
    return f"{module}.{func.__name__}"


def register_block_type(
    name: str,
    *,
    package: str = "",
    enabled: bool | None = None,
    required: bool = False,
    options: type | None = None,
    description: str = "",
    fallback: t.BlockConverter | None = None,
) -> t.BlockType:
    """
    Register a Volto block type, or complete the registration of a known one.

    The converter decorators call this function when they get a ``block_type``.
    Several converters can produce the same block type (a ``<video>`` and a
    YouTube ``<iframe>`` both become ``video``): the first registration needs the
    ``package``, and the later ones may leave the metadata out, but they may not
    contradict it.

    :param name: The Volto ``@type`` of the block.
    :param package: The frontend package that provides the block, such as
        ``@plone/volto``.
    :param enabled: Whether the block is produced when no setting mentions it.
        Blocks from add-ons are usually registered with ``False``. ``None``
        (default) keeps the state of an earlier registration, or enables a new
        block type.
    :param required: Whether the block can never be disabled.
    :param options: Dataclass with the options of the block and their defaults.
    :param description: One line describing what the block is produced from.
    :param fallback: Block converter used for the tags of the block while it is
        disabled. Without one, the tags are converted as if they had no block
        converter.
    :returns: The registered block type.
    :raises ValueError: If ``package`` is missing on the first registration, or
        if the metadata contradicts an earlier registration.

    Example:
        .. code-block:: python

            register_block_type("slate", package="@plone/volto", required=True)
    """
    block_type = _REGISTRY.block_types.get(name)
    if block_type is None:
        if not package:
            raise ValueError(f"Block type {name} needs a package")
        block_type = t.BlockType(
            name=name,
            package=package,
            enabled=True if enabled is None else enabled,
            required=required,
            options=options,
            description=description,
            fallback=fallback,
        )
        _REGISTRY.block_types[name] = block_type
    else:
        given = {
            "package": package,
            "options": options,
            "description": description,
            "fallback": fallback,
        }
        for attr, value in given.items():
            current = getattr(block_type, attr)
            if value and current and value != current:
                raise ValueError(
                    f"Block type {name} is already registered with "
                    f"{attr}={current!r}, not {value!r}"
                )
            if value and not current:
                setattr(block_type, attr, value)
        if enabled is not None and enabled != block_type.enabled:
            raise ValueError(
                f"Block type {name} is already registered with "
                f"enabled={block_type.enabled!r}, not {enabled!r}"
            )
        if required:
            block_type.required = True
    _DEFAULT_BLOCKS.clear()
    return block_type


def _bind_tag(tag_name: str, block_type: str) -> None:
    """Record that the block converter of a tag produces a block type."""
    previous = _REGISTRY.tag_block_types.pop(tag_name, "")
    if previous and tag_name in (old := _REGISTRY.block_types[previous]).tags:
        old.tags.remove(tag_name)
    if block_type:
        _REGISTRY.tag_block_types[tag_name] = block_type
        tags = _REGISTRY.block_types[block_type].tags
        if tag_name not in tags:
            tags.append(tag_name)
    _DEFAULT_BLOCKS.clear()


def _option_types(options: type) -> dict[str, Any]:
    """Return the fields of an options dataclass with their types."""
    hints = get_type_hints(options)
    return {item.name: hints[item.name] for item in dataclasses.fields(options)}


def _build_options(block_type: t.BlockType, overrides: Mapping[str, Any]) -> Any:
    """
    Build the options of a block type from the defaults and the overrides.

    :param block_type: The block type, with an options dataclass.
    :param overrides: The options given in the ``blocks`` setting.
    :returns: An instance of the options dataclass.
    :raises ValueError: For an unknown option, or a value of the wrong type.
    """
    options = cast(type, block_type.options)
    types = _option_types(options)
    for key, value in overrides.items():
        if key not in types:
            known = ", ".join(types)
            raise ValueError(
                f"Unknown option {key} for block type {block_type.name} "
                f"(options: {known})"
            )
        expected = types[key]
        valid = isinstance(value, expected) if isinstance(expected, type) else True
        if expected is int and isinstance(value, bool):
            valid = False
        if not valid:
            raise ValueError(
                f"Option {key} of block type {block_type.name} must be "
                f"{expected.__name__}, not {type(value).__name__}"
            )
    return options(**overrides)


def resolve_blocks(blocks: t.BlocksSetting | None = None) -> t.ResolvedBlocks:
    """
    Validate a ``blocks`` setting and merge it with the defaults.

    Each key of ``blocks`` is a Volto block type. ``True`` enables the block with
    its default options, a dict enables it and overrides some of its options, and
    ``False`` disables it. Block types left out keep their default state.

    :param blocks: The ``blocks`` setting, or ``None`` for the defaults.
    :returns: The enabled block types and their options.
    :raises ValueError: For an unknown block type or option, for disabling a
        required block, or for options given to a block that has none.

    Example:
        .. code-block:: pycon

            >>> resolved = resolve_blocks({"codeBlock": {"style": "light"}})
            >>> resolved.options["codeBlock"].style
            'light'
    """
    types = _REGISTRY.block_types
    enabled = {name for name, block_type in types.items() if block_type.enabled}
    overrides: dict[str, Mapping[str, Any]] = {}
    for name, value in (blocks or {}).items():
        if (block_type := types.get(name)) is None:
            known = ", ".join(sorted(types))
            raise ValueError(f"Unknown block type {name} (block types: {known})")
        if value is False:
            if block_type.required:
                raise ValueError(f"Block type {name} cannot be disabled")
            enabled.discard(name)
        elif value is True or isinstance(value, Mapping):
            enabled.add(name)
            if isinstance(value, Mapping) and value:
                if block_type.options is None:
                    raise ValueError(f"Block type {name} has no options")
                overrides[name] = value
        else:
            raise ValueError(
                f"Setting of block type {name} must be true, false or a dict of "
                f"options, not {value!r}"
            )
    options = {
        name: _build_options(types[name], overrides.get(name, {}))
        for name in enabled
        if types[name].options is not None
    }
    return t.ResolvedBlocks(enabled=frozenset(enabled), options=options)


def _current_blocks() -> t.ResolvedBlocks:
    """Return the ``blocks`` setting in effect: the conversion's, or the defaults."""
    if (current := _BLOCKS.get()) is not None:
        return current
    if not _DEFAULT_BLOCKS:
        _DEFAULT_BLOCKS.append(resolve_blocks(None))
    return _DEFAULT_BLOCKS[0]


@contextmanager
def conversion(
    blocks: t.BlocksSetting | t.ResolvedBlocks | None = None,
) -> Generator[t.ResolvedBlocks, None, None]:
    """
    Apply a ``blocks`` setting while the context is active.

    Inside the context, the tags of disabled block types go to the fallback of
    their block type, or are hidden like with :func:`hidden_block_converters`
    when there is none. Converters read their options with :func:`block_options`.

    :param blocks: The ``blocks`` setting (see :func:`resolve_blocks`), an already
        resolved one, or ``None`` for the defaults.
    :yields: The resolved setting.
    :raises ValueError: If the setting is invalid, see :func:`resolve_blocks`.

    Example:
        .. code-block:: python

            with conversion({"codeBlock": True, "slateTable": False}):
                ...
    """
    if isinstance(blocks, t.ResolvedBlocks):
        resolved = blocks
    else:
        resolved = resolve_blocks(blocks)
    token = _BLOCKS.set(resolved)
    try:
        yield resolved
    finally:
        _BLOCKS.reset(token)


def is_enabled(block_type: str) -> bool:
    """
    Return whether a block type is enabled in the conversion in progress.

    Outside a conversion, the defaults apply.

    :param block_type: The Volto ``@type`` of the block.
    :returns: ``True`` if the block is produced.
    """
    return block_type in _current_blocks().enabled


def block_options(block_type: str) -> Any:
    """
    Return the options of a block type in the conversion in progress.

    Outside a conversion, the defaults apply.

    :param block_type: The Volto ``@type`` of the block.
    :returns: An instance of the options dataclass of the block type, or ``None``
        if the block is disabled or has no options.

    Example:
        .. code-block:: python

            options = block_options("codeBlock")
            style = options.style
    """
    return _current_blocks().options.get(block_type)


def coerce_option_value(block_type: str, key: str, raw: str) -> Any:
    """
    Convert an option given as text, as on the command line, to its type.

    :param block_type: The Volto ``@type`` of the block.
    :param key: The name of the option.
    :param raw: The value as text.
    :returns: The value, converted to the type of the option.
    :raises ValueError: For an unknown block type or option, or a value that
        cannot be converted.

    Example:
        .. code-block:: pycon

            >>> coerce_option_value("codeBlock", "showLineNumbers", "yes")
            True
    """
    if (item := _REGISTRY.block_types.get(block_type)) is None:
        raise ValueError(f"Unknown block type {block_type}")
    if item.options is None:
        raise ValueError(f"Block type {block_type} has no options")
    types = _option_types(item.options)
    if key not in types:
        known = ", ".join(types)
        raise ValueError(
            f"Unknown option {key} for block type {block_type} (options: {known})"
        )
    expected = types[key]
    if expected is bool:
        if raw.lower() in _TRUE_VALUES:
            return True
        if raw.lower() in _FALSE_VALUES:
            return False
        raise ValueError(f"Option {key} of block type {block_type} must be a boolean")
    if expected in (int, float):
        try:
            return expected(raw)
        except ValueError:
            raise ValueError(
                f"Option {key} of block type {block_type} must be {expected.__name__}"
            ) from None
    return raw


def _disabled_tags() -> tuple[frozenset[str], dict[str, t.BlockConverter]]:
    """
    Return the tags affected by disabled block types.

    :returns: The tags to hide, and the fallback converter of the other ones.
    """
    enabled = _current_blocks().enabled
    hidden: set[str] = set()
    fallbacks: dict[str, t.BlockConverter] = {}
    for tag_name, name in _REGISTRY.tag_block_types.items():
        if name in enabled:
            continue
        if fallback := _REGISTRY.block_types[name].fallback:
            fallbacks[tag_name] = fallback
        else:
            hidden.add(tag_name)
    return frozenset(hidden), fallbacks


@contextmanager
def hidden_block_converters(*tag_names: str) -> Generator[None, None, None]:
    """
    Hide the block converters of some tags while the context is active.

    A hidden tag is left out of :func:`elements_with_block_converters`, and
    :func:`get_block_converter` returns ``None`` for it, so the element goes
    through the element converters or the default converter, as if no block
    converter were registered for it.

    :param tag_names: The tag names whose block converters are hidden.

    Example:
        .. code-block:: python

            with hidden_block_converters("pre"):
                ...
    """
    token = _HIDDEN_TAGS.set(_HIDDEN_TAGS.get() | frozenset(tag_names))
    try:
        yield
    finally:
        _HIDDEN_TAGS.reset(token)


class block_converter:
    """
    Decorator to register a block converter function for one or more tag names.

    With ``block_type``, the converter also declares the Volto block it produces,
    and the block can then be enabled, disabled and configured with the
    ``blocks`` setting of a conversion (see :func:`register_block_type` for the
    metadata arguments).

    :param tag_names: One or more HTML tag names to register the converter for.
    :param block_type: The Volto ``@type`` the converter produces.
    :param package: The frontend package that provides the block.
    :param enabled: Whether the block is produced when no setting mentions it.
    :param options: Dataclass with the options of the block and their defaults.
    :param description: One line describing what the block is produced from.
    :param fallback: Block converter used while the block is disabled.

    Example:
        .. code-block:: python

            @block_converter(
                "pre",
                block_type="codeBlock",
                package="@plonegovbr/volto-code-block",
                enabled=False,
            )
            def pre_block(element):
                ...
    """

    def __init__(
        self,
        *tag_names: str,
        block_type: str = "",
        package: str = "",
        enabled: bool | None = None,
        options: type | None = None,
        description: str = "",
        fallback: t.BlockConverter | None = None,
    ):
        self.tag_names = tag_names
        self.block_type = block_type
        self.metadata: dict[str, Any] = {
            "package": package,
            "enabled": enabled,
            "options": options,
            "description": description,
            "fallback": fallback,
        }

    def __call__(self, func: t.BlockConverter):
        friendly_name = f"{func.__module__}.{func.__name__}"
        if self.block_type:
            register_block_type(self.block_type, **self.metadata)
        for tag_name in self.tag_names:
            logger.debug(f"Registering block converter {friendly_name} to {tag_name}")
            _REGISTRY.block_converters[tag_name] = func
            _bind_tag(tag_name, self.block_type)
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

    With ``block_type``, the provider declares the Volto block it produces. While
    that block is disabled, its iframes go to the default provider instead, and
    while the default provider's block is disabled too, they are dropped.

    :param provider: The provider name (e.g., "youtube").
    :param src_pattern: Regex pattern for matching src URLs. Without one, the
        converter is the default provider.
    :param url_pattern: Replacement pattern for URLs.
    :param block_type: The Volto ``@type`` the provider produces.
    :param package: The frontend package that provides the block.
    :param enabled: Whether the block is produced when no setting mentions it.
    :param options: Dataclass with the options of the block and their defaults.
    :param description: One line describing what the block is produced from.

    Example:
        .. code-block:: python

            @iframe_converter("youtube", r"https://youtube.com/embed/(?P<provider_id>[^/]+)")
            def convert_youtube_iframe(element):
    """

    def __init__(
        self,
        provider: str,
        src_pattern: re.Pattern | str = "",
        url_pattern: str = "",
        block_type: str = "",
        package: str = "",
        enabled: bool | None = None,
        options: type | None = None,
        description: str = "",
    ):
        self.provider = provider
        self.src_pattern = src_pattern
        self.url_pattern = url_pattern
        self.block_type = block_type
        self.metadata: dict[str, Any] = {
            "package": package,
            "enabled": enabled,
            "options": options,
            "description": description,
        }

    def __call__(self, func: Callable):
        friendly_name = f"{func.__module__}.{func.__name__}"
        pattern = self.src_pattern if self.src_pattern else "default"
        provider = self.provider
        logger.debug(f"Registering iframe converter {friendly_name} to {provider}")
        if self.block_type:
            block_type = register_block_type(self.block_type, **self.metadata)
            if provider not in block_type.providers:
                block_type.providers.append(provider)
        converter = t.IFrameConverter(
            url_pattern=self.url_pattern,
            provider=provider,
            converter=func,
            block_type=self.block_type,
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
    disabled, _ = _disabled_tags()
    hidden = _HIDDEN_TAGS.get() | disabled
    return [tag for tag in _REGISTRY.block_converters if tag not in hidden]


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
    disabled, fallbacks = _disabled_tags()
    if tag_name in _HIDDEN_TAGS.get() or tag_name in disabled:
        converter = None
    elif tag_name in fallbacks:
        converter = fallbacks[tag_name]
    else:
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
        if pattern == "default" or not _provider_enabled(provider):
            continue
        if match := re.match(pattern, src):
            repl = provider.url_pattern
            src = cleanse_url(re.sub(pattern, repl, src))
            provider_id = match.groupdict()["provider_id"]
            return t.EmbedInfo(src, provider_id, provider.converter)
    default = converters["default"]
    if not _provider_enabled(default):
        return t.EmbedInfo(src, "", _drop_iframe)
    return t.EmbedInfo(src, "", default.converter)


def _provider_enabled(provider: t.IFrameConverter) -> bool:
    """Return whether the block type of an iframe provider is enabled."""
    return not provider.block_type or is_enabled(provider.block_type)


def _drop_iframe(element: t.Tag, src: str, provider_id: str) -> list[t.VoltoBlock]:
    """Drop an iframe whose providers are all disabled."""
    logger.debug(f"Dropping iframe {src}: its block types are disabled")
    return []


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


def _options_report(options: type | None) -> list[t.BlockOptionReport]:
    if options is None:
        return []
    types = _option_types(options)
    defaults = options()
    return [
        {
            "name": name,
            "type": getattr(type_, "__name__", str(type_)),
            "default": getattr(defaults, name),
        }
        for name, type_ in types.items()
    ]


def report_blocks() -> list[t.BlockReport]:
    """
    Return the Volto block types the converters can produce.

    Each entry gives the block type, the frontend package that provides it, its
    default state, the tags and iframe providers converted into it, its options
    with their defaults, and the converter used while it is disabled.

    :returns: One report per block type, sorted by block type.

    Example:
        .. code-block:: pycon

            >>> [item["block_type"] for item in report_blocks()]
            ['codeBlock', 'iframe', 'image', 'slate', ...]
    """
    report: list[t.BlockReport] = []
    for name in sorted(_REGISTRY.block_types, key=str.lower):
        block_type = _REGISTRY.block_types[name]
        fallback = block_type.fallback
        report.append({
            "block_type": name,
            "package": block_type.package,
            "description": block_type.description,
            "enabled": block_type.enabled,
            "required": block_type.required,
            "tags": list(block_type.tags),
            "providers": list(block_type.providers),
            "options": _options_report(block_type.options),
            "fallback": _friendly_name(fallback) if fallback else "",
        })
    return report


__all__ = [
    "block_converter",
    "block_options",
    "coerce_option_value",
    "conversion",
    "default_converter",
    "element_converter",
    "get_block_converter",
    "get_element_converter",
    "get_iframe_converter",
    "iframe_converter",
    "is_enabled",
    "register_block_type",
    "report_blocks",
    "report_registrations",
    "resolve_blocks",
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

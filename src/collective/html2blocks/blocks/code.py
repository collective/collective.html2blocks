"""
Code block converter for collective.html2blocks.

This module provides the block converter for <pre> elements, transforming them
into ``codeBlock`` blocks of ``@plonegovbr/volto-code-block``. A fenced Markdown
block and an HTML <pre> are both <pre> in the HTML the converter receives, so
one converter handles both.

The conversion is opt-in: the ``codeBlock`` type comes from an add-on, not from
Volto core. Without the option, the block converter of <pre> is hidden during
the conversion (see :func:`~collective.html2blocks.registry.hidden_block_converters`),
so the output stays exactly as it was before this converter existed.

Implementation details:
- The code is the text of the <pre> (or of its <code> child), without one
  trailing newline.
- The language comes from a ``language-*`` or ``lang-*`` class on the <code>
  or the <pre>. Common aliases are mapped to Volto language names. Without a
  language, ``text`` is used.
- The defaults for ``style``, ``wrapLongLines`` and ``showLineNumbers`` can be
  overridden with the ``code_block`` option of the converter.

Example usage::

    from collective.html2blocks.converter import volto_blocks

    info = volto_blocks(source, code_block={"style": "light"})
"""

from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.blocks.slate import slate_block
from contextvars import ContextVar
from typing import TypedDict


class CodeBlockOptions(TypedDict, total=False):
    """Options for the ``codeBlock`` blocks. Missing keys use the defaults."""

    style: str
    wrapLongLines: bool
    showLineNumbers: bool


DEFAULT_OPTIONS: CodeBlockOptions = {
    "style": "dark",
    "wrapLongLines": True,
    "showLineNumbers": False,
}

# Tags converted only when the option is enabled. Their block converters are
# hidden otherwise, so the parser sees them exactly as before.
OPT_IN_TAGS = frozenset({"pre"})

LANGUAGE_PREFIXES = ("language-", "lang-")

LANGUAGE_ALIASES = {
    "console": "bash",
    "py": "python",
    "sh": "bash",
    "shell": "bash",
}

DEFAULT_LANGUAGE = "text"

# Options of the conversion in progress; ``None`` means the option is disabled.
OPTIONS: ContextVar[CodeBlockOptions | None] = ContextVar(
    "code_block_options", default=None
)


def resolve_options(code_block: CodeBlockOptions | None) -> CodeBlockOptions | None:
    """
    Merge the given options with the defaults.

    :param code_block: The options given by the caller, or ``None`` to disable the
        conversion. An empty dict enables it with the defaults.
    :returns: The merged options, or ``None`` when the conversion is disabled.

    Example::

        >>> resolve_options({"style": "light"})["wrapLongLines"]
        True
    """
    if code_block is None:
        return None
    return {**DEFAULT_OPTIONS, **code_block}


def _language(element: t.Tag, code_element: t.Tag | None) -> str:
    """
    Return the Volto language name for a <pre> element.

    :param element: The <pre> element.
    :param code_element: The <code> child of the <pre>, if any.
    :returns: The language name, ``text`` when none is declared.
    """
    for candidate in (code_element, element):
        if candidate is None:
            continue
        classes = candidate.get("class") or []
        if isinstance(classes, str):
            classes = classes.split()
        for css_class in classes:
            for prefix in LANGUAGE_PREFIXES:
                if css_class.startswith(prefix) and len(css_class) > len(prefix):
                    name = css_class[len(prefix) :].lower()
                    return LANGUAGE_ALIASES.get(name, name)
    return DEFAULT_LANGUAGE


@registry.block_converter("pre")
def pre_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """
    Convert a <pre> element to a ``codeBlock`` block, when the option is enabled.

    When the option is disabled, the element is converted by the default slate
    converter, as it was before this converter was registered.

    :param element: The <pre> element to convert.
    :yields: The ``codeBlock`` block, or the default slate block when disabled.

    Example::

        blocks = list(pre_block(element))
        # [{'@type': 'codeBlock', 'code': 'x = 1', 'language': 'python', ...}]
    """
    options = OPTIONS.get()
    if options is None:
        # Hidden while converting, so the default converter does not come back here.
        with registry.hidden_block_converters(*OPT_IN_TAGS):
            yield from slate_block(element)
        return
    code_element = element.find("code")
    if not isinstance(code_element, t.Tag):
        code_element = None
    source = code_element if code_element is not None else element
    code = source.get_text().removesuffix("\n")
    yield {
        "@type": "codeBlock",
        "code": code,
        "language": _language(element, code_element),
        "showLineNumbers": options["showLineNumbers"],
        "lineNbr": 1,
        "style": options["style"],
        "wrapLongLines": options["wrapLongLines"],
    }

"""
Code block converter for collective.html2blocks.

This module provides the block converter for <pre> elements, transforming them
into ``codeBlock`` blocks of ``@plonegovbr/volto-code-block``. A fenced Markdown
block and an HTML <pre> are both <pre> in the HTML the converter receives, so
one converter handles both.

The ``codeBlock`` block type is disabled by default: it comes from an add-on, not
from Volto core. While it is disabled, the block converter of <pre> is hidden
during the conversion, so the output stays exactly as it was before this
converter existed.

Implementation details:
- The code is the text of the <pre> (or of its <code> child), without one
  trailing newline.
- The language comes from a ``language-*`` or ``lang-*`` class on the <code>
  or the <pre>. Common aliases are mapped to Volto language names. Without a
  language, ``text`` is used.
- The defaults for ``style``, ``wrapLongLines`` and ``showLineNumbers`` are the
  fields of :class:`CodeBlockOptions`, overridden with the ``blocks`` setting.

Example usage::

    from collective.html2blocks.converter import volto_blocks

    info = volto_blocks(source, blocks={"codeBlock": {"style": "light"}})
"""

from collections.abc import Generator
from collective.html2blocks import _types as t
from collective.html2blocks import registry
from collective.html2blocks.blocks.slate import slate_block
from dataclasses import dataclass


BLOCK_TYPE = "codeBlock"


@dataclass(frozen=True)
class CodeBlockOptions:
    """Options of the ``codeBlock`` blocks."""

    style: str = "dark"
    wrapLongLines: bool = True
    showLineNumbers: bool = False


LANGUAGE_PREFIXES = ("language-", "lang-")

LANGUAGE_ALIASES = {
    "console": "bash",
    "py": "python",
    "sh": "bash",
    "shell": "bash",
}

DEFAULT_LANGUAGE = "text"


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


@registry.block_converter(
    "pre",
    block_type=BLOCK_TYPE,
    package="@plonegovbr/volto-code-block",
    enabled=False,
    options=CodeBlockOptions,
    description="Code: HTML <pre> and Markdown code fences or indented code.",
)
def pre_block(element: t.Tag) -> Generator[t.VoltoBlock, None, None]:
    """
    Convert a <pre> element to a ``codeBlock`` block, when the block is enabled.

    During a conversion, a disabled ``codeBlock`` hides this converter, so it is
    only called with the block enabled. Called directly while the block is
    disabled, it falls back to the default slate converter.

    :param element: The <pre> element to convert.
    :yields: The ``codeBlock`` block, or the default slate block when disabled.

    Example::

        blocks = list(pre_block(element))
        # [{'@type': 'codeBlock', 'code': 'x = 1', 'language': 'python', ...}]
    """
    options: CodeBlockOptions | None = registry.block_options(BLOCK_TYPE)
    if options is None:
        # Hidden while converting, so the default converter does not come back here.
        with registry.hidden_block_converters("pre"):
            yield from slate_block(element)
        return
    code_element = element.find("code")
    if not isinstance(code_element, t.Tag):
        code_element = None
    source = code_element if code_element is not None else element
    code = source.get_text().removesuffix("\n")
    yield {
        "@type": BLOCK_TYPE,
        "code": code,
        "language": _language(element, code_element),
        "showLineNumbers": options.showLineNumbers,
        "lineNbr": 1,
        "style": options.style,
        "wrapLongLines": options.wrapLongLines,
    }

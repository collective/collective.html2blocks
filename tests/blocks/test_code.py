from collective.html2blocks import converter
from collective.html2blocks import registry

import pytest


HTML_PRE = "<p>Before</p><pre>uv add plone-client\n</pre><p>After</p>"
HTML_PRE_CODE_CLASS = '<pre><code class="language-python">print(1)\n</code></pre>'
MARKDOWN_FENCE = "```shell\nuv add plone-client\n```\n"
MARKDOWN_INDENTED = "Intro\n\n    indented code\n    more\n\nOutro\n"


def _blocks(info: dict) -> list:
    """Return the blocks of a Volto info structure in layout order."""
    return [info["blocks"][item] for item in info["blocks_layout"]["items"]]


def _code_blocks(info: dict) -> list:
    """Return only the codeBlock blocks of a Volto info structure."""
    return [block for block in _blocks(info) if block["@type"] == "codeBlock"]


@pytest.mark.parametrize(
    "source,source_format,expected_code,expected_language",
    [
        [MARKDOWN_FENCE, "markdown", "uv add plone-client", "bash"],
        [MARKDOWN_INDENTED, "markdown", "indented code\nmore", "text"],
        [HTML_PRE, "html", "uv add plone-client", "text"],
        [HTML_PRE_CODE_CLASS, "html", "print(1)", "python"],
    ],
)
def test_code_block_converted(
    source: str, source_format: str, expected_code: str, expected_language: str
):
    info = converter.volto_blocks(source, source_format=source_format, code_block={})
    blocks = _code_blocks(info)
    assert len(blocks) == 1
    assert blocks[0] == {
        "@type": "codeBlock",
        "code": expected_code,
        "language": expected_language,
        "showLineNumbers": False,
        "lineNbr": 1,
        "style": "dark",
        "wrapLongLines": True,
    }


def test_code_block_keeps_surrounding_blocks():
    info = converter.volto_blocks(HTML_PRE, code_block={})
    types = [block["@type"] for block in _blocks(info)]
    assert types == ["slate", "codeBlock", "slate"]
    assert _blocks(info)[0]["plaintext"] == "Before"
    assert _blocks(info)[2]["plaintext"] == "After"


@pytest.mark.parametrize(
    "source,expected",
    [
        ['<pre class="language-py">x = 1\n</pre>', "python"],
        ['<pre class="lang-js">x = 1\n</pre>', "js"],
        ['<pre><code class="lang-go">x\n</code></pre>', "go"],
        ['<pre><code class="language-shell">x\n</code></pre>', "bash"],
        ['<pre><code class="language-sh">x\n</code></pre>', "bash"],
        ['<pre><code class="language-console">x\n</code></pre>', "bash"],
        ['<pre><code class="language-py">x\n</code></pre>', "python"],
        ['<pre><code class="language-Python">x\n</code></pre>', "python"],
        ['<pre><code class="hljs language-html">x\n</code></pre>', "html"],
        ['<pre><code class="language-">x\n</code></pre>', "text"],
        ['<pre><code class="highlight">x\n</code></pre>', "text"],
    ],
)
def test_code_block_language(source: str, expected: str):
    info = converter.volto_blocks(source, code_block={})
    assert _code_blocks(info)[0]["language"] == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ["<pre>one line\n</pre>", "one line"],
        ["<pre>one line</pre>", "one line"],
        ["<pre>first\nsecond\n</pre>", "first\nsecond"],
        ["<pre>keeps two\n\n</pre>", "keeps two\n"],
    ],
)
def test_code_block_trailing_newline(source: str, expected: str):
    info = converter.volto_blocks(source, code_block={})
    assert _code_blocks(info)[0]["code"] == expected


def test_code_block_options_override_defaults():
    info = converter.volto_blocks(
        HTML_PRE,
        code_block={"style": "light", "wrapLongLines": False, "showLineNumbers": True},
    )
    block = _code_blocks(info)[0]
    assert block["style"] == "light"
    assert block["wrapLongLines"] is False
    assert block["showLineNumbers"] is True


def test_code_block_partial_options_keep_other_defaults():
    info = converter.volto_blocks(HTML_PRE, code_block={"style": "light"})
    block = _code_blocks(info)[0]
    assert block["style"] == "light"
    assert block["wrapLongLines"] is True
    assert block["showLineNumbers"] is False


@pytest.mark.parametrize(
    "source,source_format",
    [
        [HTML_PRE, "html"],
        [HTML_PRE_CODE_CLASS, "html"],
        [MARKDOWN_FENCE, "markdown"],
        [MARKDOWN_INDENTED, "markdown"],
    ],
)
def test_default_output_keeps_pre_as_slate(source: str, source_format: str):
    """Without the option, code stays a slate block, as before the converter."""
    info = converter.volto_blocks(source, source_format=source_format)
    assert _code_blocks(info) == []
    assert all(block["@type"] == "slate" for block in _blocks(info))


def test_default_output_pins_fence_slate_shape():
    """Pin the slate shape of a Markdown fence while the option is off."""
    info = converter.volto_blocks(MARKDOWN_FENCE, source_format="markdown")
    blocks = _blocks(info)
    assert len(blocks) == 1
    assert blocks[0]["@type"] == "slate"
    assert blocks[0]["plaintext"] == "uv add plone-client"
    assert blocks[0]["value"] == [
        {
            "type": "p",
            "children": [{"type": "code", "text": "uv add plone-client\n"}],
        }
    ]


@pytest.mark.parametrize(
    "source,expected",
    [
        ["<p>one <pre>two</pre> three</p>", [("slate", "one two three")]],
        [
            "<div><p>a</p><pre>x = 1\n</pre><p>b</p></div>",
            [("slate", "a"), ("slate", "x = 1"), ("slate", "b")],
        ],
        ["<section><p>s</p><pre>sec</pre></section>", [("slate", "ssec")]],
        ["<pre>top level</pre>", [("slate", "top level")]],
    ],
)
def test_default_output_keeps_pre_layout(source: str, expected: list):
    """
    Pin the block layout of <pre> inside other elements while the option is off.

    Registering a block converter for <pre> would split paragraphs and unwrap
    containers around it, so these layouts only hold while the converter is hidden.
    """
    info = converter.volto_blocks(source)
    layout = [(block["@type"], block.get("plaintext")) for block in _blocks(info)]
    assert layout == expected


def test_default_output_pins_html_pre_slate_shape():
    """Pin the slate shape of an HTML <pre> while the option is off."""
    info = converter.volto_blocks(HTML_PRE)
    pre = _blocks(info)[1]
    assert pre["@type"] == "slate"
    assert pre["value"] == [
        {"type": "pre", "children": [{"text": "uv add plone-client "}]}
    ]


def test_default_output_equals_explicit_none(strip_keys):
    default = converter.volto_blocks(HTML_PRE)
    explicit = converter.volto_blocks(HTML_PRE, code_block=None)
    assert strip_keys(_blocks(default)) == strip_keys(_blocks(explicit))


def test_pre_converter_hidden_only_during_default_conversion():
    """The converter stays registered; hiding it lasts for one conversion only."""
    converter.volto_blocks(HTML_PRE)
    assert registry.get_block_converter(tag_name="pre") is not None
    assert "pre" in registry.elements_with_block_converters()


def test_html_to_blocks_accepts_code_block():
    blocks = converter.html_to_blocks(HTML_PRE, code_block={})
    assert [block["@type"] for block in blocks] == ["slate", "codeBlock", "slate"]
    assert [block["@type"] for block in converter.html_to_blocks(HTML_PRE)] == [
        "slate",
        "slate",
        "slate",
    ]

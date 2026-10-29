from collective.html2blocks import converter
from collective.html2blocks import registry
from collective.html2blocks.blocks.code import pre_block

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
    info = converter.volto_blocks(
        source, source_format=source_format, blocks={"codeBlock": True}
    )
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
    info = converter.volto_blocks(HTML_PRE, blocks={"codeBlock": True})
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
    info = converter.volto_blocks(source, blocks={"codeBlock": True})
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
    info = converter.volto_blocks(source, blocks={"codeBlock": True})
    assert _code_blocks(info)[0]["code"] == expected


def test_code_block_options_override_defaults():
    info = converter.volto_blocks(
        HTML_PRE,
        blocks={
            "codeBlock": {
                "style": "light",
                "wrapLongLines": False,
                "showLineNumbers": True,
            }
        },
    )
    block = _code_blocks(info)[0]
    assert block["style"] == "light"
    assert block["wrapLongLines"] is False
    assert block["showLineNumbers"] is True


def test_code_block_partial_options_keep_other_defaults():
    info = converter.volto_blocks(HTML_PRE, blocks={"codeBlock": {"style": "light"}})
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


@pytest.mark.parametrize("setting", [None, {}, {"codeBlock": False}])
def test_default_output_equals_explicit_disabled(strip_keys, setting):
    default = converter.volto_blocks(HTML_PRE)
    explicit = converter.volto_blocks(HTML_PRE, blocks=setting)
    assert strip_keys(_blocks(default)) == strip_keys(_blocks(explicit))


def test_pre_converter_follows_the_setting():
    """The converter stays registered; the setting decides whether it is used."""
    converter.volto_blocks(HTML_PRE, blocks={"codeBlock": True})
    assert registry.get_block_converter(tag_name="pre") is None
    assert "pre" not in registry.elements_with_block_converters()
    with registry.conversion({"codeBlock": True}):
        assert registry.get_block_converter(tag_name="pre") is pre_block
        assert "pre" in registry.elements_with_block_converters()
    assert "pre" in registry.report_registrations()["block"]


def test_html_to_blocks_accepts_blocks():
    blocks = converter.html_to_blocks(HTML_PRE, blocks={"codeBlock": True})
    assert [block["@type"] for block in blocks] == ["slate", "codeBlock", "slate"]
    assert [block["@type"] for block in converter.html_to_blocks(HTML_PRE)] == [
        "slate",
        "slate",
        "slate",
    ]


def test_pre_in_table_comes_after_the_table():
    """Like images, code cannot live in a table cell, and follows the table."""
    source = "<table><tr><td><pre><code>x = 1</code></pre></td></tr></table>"
    blocks = converter.html_to_blocks(source, blocks={"codeBlock": True})
    assert [block["@type"] for block in blocks] == ["slateTable", "codeBlock"]
    assert blocks[1]["code"] == "x = 1"


@pytest.mark.parametrize(
    "func,source,kwargs",
    [
        [converter.html_to_blocks, HTML_PRE, {}],
        [converter.markdown_to_blocks, MARKDOWN_FENCE, {}],
        [converter.volto_blocks, HTML_PRE, {}],
        [converter.volto_blocks, MARKDOWN_FENCE, {"source_format": "markdown"}],
    ],
)
def test_blocks_options_in_every_entry_point(func, source: str, kwargs: dict):
    result = func(source, blocks={"codeBlock": {"style": "light"}}, **kwargs)
    blocks = _blocks(result) if func is converter.volto_blocks else result
    assert [block["style"] for block in blocks if block["@type"] == "codeBlock"] == [
        "light"
    ]


@pytest.mark.parametrize(
    "func", [converter.html_to_blocks, converter.markdown_to_blocks]
)
def test_code_block_argument_removed(func):
    with pytest.raises(TypeError, match="code_block"):
        func(HTML_PRE, code_block={})


@pytest.mark.parametrize(
    "setting,match",
    [
        [{"codeBlock": {"wrap_long_lines": False}}, "Unknown option wrap_long_lines"],
        [{"codeBlock": {"style": 1}}, "must be str, not int"],
        [{"codeBlock": {"showLineNumbers": "yes"}}, "must be bool, not str"],
        [{"codeBlock": "on"}, "must be true, false or a dict"],
    ],
)
def test_invalid_code_block_options(setting: dict, match: str):
    with pytest.raises(ValueError, match=match):
        converter.html_to_blocks(HTML_PRE, blocks=setting)

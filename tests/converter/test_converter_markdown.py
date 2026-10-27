from collective.html2blocks import converter

import pytest


CASES = [
    (
        "heading",
        "# Title\n\n## Subtitle\n",
        "<h1>Title</h1>\n<h2>Subtitle</h2>",
    ),
    (
        "paragraph",
        "Hello **world**.\n\nSecond paragraph.",
        "<p>Hello <strong>world</strong>.</p>\n<p>Second paragraph.</p>",
    ),
    (
        "list",
        "- one\n- two\n",
        "<ul>\n<li>one</li>\n<li>two</li>\n</ul>",
    ),
    (
        "link",
        "See [the site](https://example.org).",
        '<p>See <a href="https://example.org">the site</a>.</p>',
    ),
    (
        "emphasis",
        "*emphasis* and ~~strikethrough~~",
        "<p><em>emphasis</em> and <s>strikethrough</s></p>",
    ),
    (
        "inline code",
        "Call `run()` now.",
        "<p>Call <code>run()</code> now.</p>",
    ),
    (
        "code block",
        "```python\nprint(1)\n```",
        '<pre><code class="language-python">print(1)\n</code></pre>',
    ),
    (
        "image",
        "![An alt text](https://example.org/image.png)",
        '<p><img src="https://example.org/image.png" alt="An alt text" /></p>',
    ),
    (
        "table",
        "| a | **b** |\n|:--|--:|\n| `1` | [x](https://example.org) |\n",
        '<table>\n<thead>\n<tr>\n<th style="text-align:left">a</th>\n'
        '<th style="text-align:right"><strong>b</strong></th>\n</tr>\n</thead>\n'
        "<tbody>\n<tr>\n"
        '<td style="text-align:left"><code>1</code></td>\n'
        '<td style="text-align:right"><a href="https://example.org">x</a></td>\n'
        "</tr>\n</tbody>\n</table>",
    ),
]


@pytest.mark.parametrize(
    "markdown,html",
    [(case[1], case[2]) for case in CASES],
    ids=[case[0] for case in CASES],
)
def test_markdown_to_blocks_matches_html(strip_keys, markdown: str, html: str):
    blocks = converter.markdown_to_blocks(markdown)
    expected = converter.html_to_blocks(html)
    assert blocks, "Markdown produced no blocks"
    assert strip_keys(blocks) == strip_keys(expected)


@pytest.mark.parametrize(
    "markdown,html",
    [(case[1], case[2]) for case in CASES],
    ids=[case[0] for case in CASES],
)
def test_volto_blocks_markdown_source_format(strip_keys, markdown: str, html: str):
    result = converter.volto_blocks(markdown, source_format="markdown")
    expected = converter.volto_blocks(html)
    items = result["blocks_layout"]["items"]
    assert items, "Markdown produced no layout items"
    assert len(items) == len(expected["blocks_layout"]["items"])
    assert [strip_keys(result["blocks"][item]) for item in items] == [
        strip_keys(expected["blocks"][item])
        for item in expected["blocks_layout"]["items"]
    ]


def test_volto_blocks_default_source_format_is_html(strip_keys):
    html = "<p>Hello <strong>world</strong>!</p>"
    default = converter.volto_blocks(html)
    explicit = converter.volto_blocks(html, source_format="html")
    assert len(default["blocks_layout"]["items"]) == len(
        explicit["blocks_layout"]["items"]
    )
    default_blocks = [
        strip_keys(default["blocks"][i]) for i in default["blocks_layout"]["items"]
    ]
    explicit_blocks = [
        strip_keys(explicit["blocks"][i]) for i in explicit["blocks_layout"]["items"]
    ]
    assert default_blocks
    assert default_blocks == explicit_blocks


def test_volto_blocks_markdown_is_not_html():
    """Markdown read as HTML keeps its markup characters, so the outputs differ."""
    markdown = "# Title"
    as_markdown = converter.volto_blocks(markdown, source_format="markdown")
    as_html = converter.volto_blocks(markdown, source_format="html")
    assert as_markdown != as_html


def test_volto_blocks_unknown_source_format():
    with pytest.raises(ValueError, match="Unsupported source format: rst"):
        converter.volto_blocks("# Title", source_format="rst")

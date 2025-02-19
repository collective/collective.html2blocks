import pytest


@pytest.mark.parametrize(
    "src,expected_type",
    [
        [
            '<img src="https://plone.org/news/item" title="A Picture" alt="Picture of a person" class="lazy-load">',
            "image",
        ],
    ],
)
def test_slate_block_defer(block_factory, src: str, expected_type: str):
    results = block_factory(src)
    assert isinstance(results, list)
    result = results[0]
    assert isinstance(result, dict)
    assert result["@type"] == expected_type


PARAMS = {
    "Simple paragraph": {
        "src": "<p>Hello World!</p>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello World!"],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Hello World!"],
        ],
    },
    "Strong block": {
        "src": "<b>Hello World!</b>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello World!"],
            ["0/value/0/type", "strong"],
            ["0/value/0/children/0/text", "Hello World!"],
        ],
    },
    "Plaintext trims string": {
        "src": "<b> Hello World! </b>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello World!"],
            ["0/value/0/type", "strong"],
            ["0/value/0/children/0/text", " Hello World! "],
        ],
    },
    "Paragraph with nested strong": {
        "src": "<p><b> Hello World! </b><br></p>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello World!"],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/type", "strong"],
            ["0/value/0/children/0/children/0/text", " Hello World! "],
        ],
    },
    "Nested structure of elements": {
        "src": '<p><strong>Arrival by car:</strong> A 1 Autobahn network (East and West) easily accessible from all directions (toll sticker - compulsory „Vignette“ - required on all motorways!) to St. Pölten then take the  <span class="renderable-component">L5122 till Neidling </span></p>',
        "tests": [
            ["0/@type", "slate"],
            [
                "0/plaintext",
                "Arrival by car: A 1 Autobahn network (East and West) easily accessible from all directions (toll sticker - compulsory „Vignette“ - required on all motorways!) to St. Pölten then take the  L5122 till Neidling",
            ],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/type", "strong"],
            ["0/value/0/children/0/children/0/text", "Arrival by car:"],
            [
                "0/value/0/children/1/text",
                " A 1 Autobahn network (East and West) easily accessible from all directions (toll sticker - compulsory „Vignette“ - required on all motorways!) to St. Pölten then take the  L5122 till Neidling ",
            ],
        ],
    },
    "Nested structure of elements including link": {
        "src": '<p><strong>Follow Plone and Plone Conference on Twitter <a href="https://twitter.com/plone" title="Plone Twitter">@plone</a> and <a href="https://twitter.com/ploneconf" title="Twitter">@ploneconf</a> and hastag #ploneconf2021</strong></p>',
        "tests": [
            ["0/@type", "slate"],
            [
                "0/plaintext",
                "Follow Plone and Plone Conference on Twitter @plone and @ploneconf and hastag #ploneconf2021",
            ],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/type", "strong"],
            [
                "0/value/0/children/0/children/0/text",
                "Follow Plone and Plone Conference on Twitter ",
            ],
            ["0/value/0/children/0/children/1/type", "link"],
            ["0/value/0/children/0/children/1/children/0/text", "@plone"],
            ["0/value/0/children/0/children/1/data/target", None],
            ["0/value/0/children/0/children/1/data/title", "Plone Twitter"],
            ["0/value/0/children/0/children/1/data/url", "https://twitter.com/plone"],
            ["0/value/0/children/0/children/2/text", " and "],
            ["0/value/0/children/0/children/3/type", "link"],
            ["0/value/0/children/0/children/3/children/0/text", "@ploneconf"],
            ["0/value/0/children/0/children/3/data/target", None],
            ["0/value/0/children/0/children/3/data/title", "Twitter"],
            [
                "0/value/0/children/0/children/3/data/url",
                "https://twitter.com/ploneconf",
            ],
            ["0/value/0/children/0/children/4/text", " and hastag #ploneconf2021"],
        ],
    },
    "With whitespace between inline elements": {
        "src": "<p><em>em</em> <strong>strong</strong></p>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "em strong"],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/type", "em"],
            ["0/value/0/children/0/children/0/text", "em"],
            ["0/value/0/children/1/text", " "],
            ["0/value/0/children/2/type", "strong"],
            ["0/value/0/children/2/children/0/text", "strong"],
        ],
    },
    "With old TinyMCE settings for bold": {
        "src": '<p>Normal Text <span style="font-weight: bold;">Bold Text</span> more normal text</p>',
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Normal Text Bold Text more normal text"],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Normal Text "],
            ["0/value/0/children/1/type", "strong"],
            ["0/value/0/children/1/children/0/text", "Bold Text"],
            ["0/value/0/children/2/text", " more normal text"],
        ],
    },
    "With old TinyMCE settings for italic": {
        "src": '<p>Normal Text <span style="font-style: italic;">Italic Text</span> more normal text</p>',
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Normal Text Italic Text more normal text"],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Normal Text "],
            ["0/value/0/children/1/type", "em"],
            ["0/value/0/children/1/children/0/text", "Italic Text"],
            ["0/value/0/children/2/text", " more normal text"],
        ],
    },
    "With an empty bold element in the text": {
        "src": "<p>Hello world!<b></b></p>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a simple pre block": {
        "src": "<pre>Plone Foundation: https://plone.org/</pre>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Plone Foundation: https://plone.org/"],
            ["0/value/0/type", "pre"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Plone Foundation: https://plone.org/"],
        ],
    },
    "Processing a pre block with nested code element": {
        "src": "<pre><code>import this</code></pre>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "import this"],
            ["0/value/0/type", "code"],
            ["0/value/0/text", "import this"],
        ],
    },
    "Processing a br": {
        "src": "<br>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", ""],
            ["len:0/value", 1],
            ["0/value/0/text", "\n"],
        ],
    },
    "Processing a code element": {
        "src": "<code>import this</code>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "import this"],
            ["0/value/0/type", "code"],
            ["0/value/0/text", "import this"],
        ],
    },
    "Processing a blockquote block": {
        "src": '<blockquote cite="https://www.huxley.net/bnw/four.html"><p>Words can be like X-rays, if you use them properly—they’ll go through anything. You read and you’re pierced.</p></blockquote>',
        "tests": [
            ["0/@type", "slate"],
            [
                "0/plaintext",
                "Words can be like X-rays, if you use them properly—they’ll go through anything. You read and you’re pierced.",
            ],
            ["0/value/0/type", "blockquote"],
            ["len:0/value/0/children", 1],
            [
                "0/value/0/children/0/text",
                "Words can be like X-rays, if you use them properly—they’ll go through anything. You read and you’re pierced.",
            ],
        ],
    },
    "Processing a span": {
        "src": "<span>Hello world!</span>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/text", "Hello world!"],
        ],
    },
    "Processing a span with a line break": {
        "src": "<span>\n</span>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", ""],
            ["0/value/0/text", " "],
        ],
    },
    "Processing a span without children nodes": {
        "src": "<span></span>",
        "tests": [
            ["", []],
        ],
    },
    "Processing a span with other inline elements": {
        "src": "<span>Hola <strong>world</strong>!</span>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hola world!"],
            ["len:0/value", 3],
            ["0/value/0/text", "Hola "],
            ["0/value/1/type", "strong"],
            ["0/value/1/children/0/text", "world"],
            ["0/value/2/text", "!"],
        ],
    },
    "Processing a span with google docs style for sup": {
        "src": '<span style="vertical-align:sup">Hallo world!</span>',
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hallo world!"],
            ["len:0/value", 1],
            ["0/value/0/type", "sup"],
            ["0/value/0/children/0/text", "Hallo world!"],
        ],
    },
    "Processing a span inside another element with an empty value will drop empty span": {
        "src": "<p><span>Foo</span><span></span></p>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Foo"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Foo"],
        ],
    },
    "Processing a div": {
        "src": "<div>Ciao world!</div>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Ciao world!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Ciao world!"],
        ],
    },
    "Processing a div with a nested paragraph value": {
        "src": "<div><p>Ciao world!</p></div>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Ciao world!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Ciao world!"],
        ],
    },
    "Processing a div with nested paragraphs": {
        "src": "<div><p>Hello</p> <p>world!</p></div>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["len:0/value", 3],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Hello"],
            ["0/value/1/type", "p"],
            ["0/value/1/children/0/text", " "],
            ["0/value/2/type", "p"],
            ["0/value/2/children/0/text", "world!"],
        ],
    },
    "Processing a div with a nested div": {
        "src": "<div><div>Ciao world!</p></div>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Ciao world!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Ciao world!"],
        ],
    },
    "Processing a div with a nested div and nested paragraphs": {
        "src": "<div><div><p>Hello</p> <p>world!</p></div></div>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["len:0/value", 3],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Hello"],
            ["0/value/1/type", "p"],
            ["0/value/1/children/0/text", " "],
            ["0/value/2/type", "p"],
            ["0/value/2/children/0/text", "world!"],
        ],
    },
    "Processing a h1": {
        "src": "<h1>Hello world!</h1>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "h1"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a h2": {
        "src": "<h2>Hello world!</h2>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "h2"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a h2 will ignore img element in the structure": {
        "src": '<h2 id="chrissy"><img src="https://plone.org/foundation/meetings/membership/2019-membership-meeting/nominations/img4_08594.jpg/@@images/7a07f0e5-0fd7-4366-a32d-6b033c8dfce7.jpeg" title="Chrissy Wainwright 2019" alt="Chrissy Wainwright 2019" class="image-right">Chrissy Wainwright</h2>',
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Chrissy Wainwright"],
            ["len:0/value", 2],
            ["0/value/0/type", "h2"],
            ["0/value/0/children/0/text", "Chrissy Wainwright"],
            ["0/value/1/@type", "image"],
        ],
    },
    "Processing a b": {
        "src": "<b>Hello world!</b>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "strong"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a strong": {
        "src": "<strong>Hello world!</strong>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "strong"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a strong with empty content": {
        "src": "<strong></strong>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", ""],
            ["0/value/0/text", ""],
        ],
    },
    "Processing a strike": {
        "src": "<s>Hello world!</s>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "s"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing an italic with i tag": {
        "src": "<i>Hello world!</i>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "em"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing an italic with em tag": {
        "src": "<em>Hello world!</em>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "em"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing an ordered list": {
        "src": "<ol><li>Item 1</li><li>Item 2</li></ol>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Item 1 Item 2"],
            ["0/value/0/type", "ol"],
            ["len:0/value/0/children", 2],
            ["0/value/0/children/0/type", "li"],
            ["0/value/0/children/0/children/0/text", "Item 1"],
            ["0/value/0/children/1/type", "li"],
            ["0/value/0/children/1/children/0/text", "Item 2"],
        ],
    },
    "Processing an unordered list": {
        "src": "<ul><li>Item 1</li><li>Item 2</li></ul>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Item 1 Item 2"],
            ["0/value/0/type", "ul"],
            ["len:0/value/0/children", 2],
            ["0/value/0/children/0/type", "li"],
            ["0/value/0/children/0/children/0/text", "Item 1"],
            ["0/value/0/children/1/type", "li"],
            ["0/value/0/children/1/children/0/text", "Item 2"],
        ],
    },
    "Processing a sub": {
        "src": "<sub>Hello world!</sub>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "sub"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a sup": {
        "src": "<sup>Hello world!</sup>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Hello world!"],
            ["0/value/0/type", "sup"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Hello world!"],
        ],
    },
    "Processing a hr": {
        "src": "<hr>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", ""],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", ""],
        ],
    },
    "Processing a link": {
        "src": '<a href="https://plone.org/" title="Plone website" target="_blank">Welcome to Plone!</a>',
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Welcome to Plone!"],
            ["0/value/0/type", "link"],
            ["0/value/0/data/url", "https://plone.org/"],
            ["0/value/0/data/title", "Plone website"],
            ["0/value/0/data/target", "_blank"],
            ["0/value/0/children/0/text", "Welcome to Plone!"],
        ],
    },
    "Processing a paragraph with additional css class": {
        "src": '<p class="anyotherclass">Paragraph with any other class name</p>',
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Paragraph with any other class name"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Paragraph with any other class name"],
        ],
    },
    "Paragraph with two spans": {
        "src": "<p><span>Olaa</span> <span>World!</span></p>",
        "tests": [
            ["0/@type", "slate"],
            ["0/plaintext", "Olaa World!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Olaa World!"],
        ],
    },
}


@pytest.mark.parametrize(
    "name,src,path,expected",
    [[k, PARAMS[k]["src"], *v] for k in PARAMS for v in PARAMS[k]["tests"]],
)
def test_slate_block(block_factory, traverse, name, src, path, expected):
    results = block_factory(src)
    if path == "":
        # Empty block
        assert results == expected
    else:
        value = traverse(results, path)
        assert value == expected, f"{name}: {value} != {expected}"

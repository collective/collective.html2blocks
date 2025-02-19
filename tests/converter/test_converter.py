from collective.html2blocks import converter

import pytest


PARAMS = {
    "div with one paragraph": {
        "src": "<div><p>Hello World!</p></div>",
        "tests": [
            ["len:", 1],
            ["0/@type", "slate"],
            ["0/plaintext", "Hello World!"],
            ["len:0/value", 1],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Hello World!"],
        ],
    },
    "div with two paragraphs": {
        "src": "<div><p>Hello</p> <p>World!</p></div>",
        "tests": [
            ["len:", 3],
            ["0/@type", "slate"],
            ["0/plaintext", "Hello"],
            ["0/value/0/type", "p"],
            ["0/value/0/children/0/text", "Hello"],
            ["1/@type", "slate"],
            ["1/plaintext", ""],
            ["1/value/0/type", "p"],
            ["1/value/0/children/0/text", " "],
            ["2/@type", "slate"],
            ["2/plaintext", "World!"],
            ["2/value/0/type", "p"],
            ["2/value/0/children/0/text", "World!"],
        ],
    },
    "div with two spans": {
        "src": "<div><span>Olaa</span> <span>World!</span></div>",
        "tests": [
            ["len:", 1],
            ["0/@type", "slate"],
            ["0/plaintext", "Olaa World!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Olaa World!"],
        ],
    },
    "Paragraph with two spans": {
        "src": "<p><span>Olaa</span> <span>World!</span></p>",
        "tests": [
            ["len:", 1],
            ["0/@type", "slate"],
            ["0/plaintext", "Olaa World!"],
            ["0/value/0/type", "p"],
            ["len:0/value/0/children", 1],
            ["0/value/0/children/0/text", "Olaa World!"],
        ],
    },
    "Paragraph with image": {
        "src": '<p><span>Olaa</span> <span>World!</span><img src="https://plone.org/news/item" title="A Picture" alt="Picture of a person" class="lazy-load"></p>',
        "tests": [
            ["len:", 2],
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
def test_html_to_blocks(traverse, name, src, path, expected):
    result = converter.html_to_blocks(src)
    assert isinstance(result, list)
    if path == "":
        assert result is expected
    else:
        value = traverse(result, path)
        assert value == expected, f"{name}: {value} != {expected}"

import pytest


PARAMS = {
    "Table with br": {
        "src": '<table class="plain">\n<tbody>\n<tr><td><br/>Text</td></tr>\n</tbody>\n</table>',
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/hideHeaders", True],
            ["0/table/inverted", False],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            ["0/table/rows/1/cells/0/value", [{"text": "\nText"}]],
        ],
    },
    "Table with div": {
        "src": "<table><tr><td><div><strong>text</strong></div></td></tr></table>",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [{"children": [{"text": "text"}], "type": "strong"}],
            ],
        ],
    },
    "Table with link": {
        "src": '<table><tr><td><a href="https://plone.org">Plone</a></td></tr></table>',
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [
                    {
                        "children": [{"text": "Plone"}],
                        "data": {
                            "target": None,
                            "title": None,
                            "url": "https://plone.org",
                        },
                        "type": "link",
                    }
                ],
            ],
        ],
    },
    "Table settings, no ui": {
        "src": '<table class="celled fixed striped very basic compact"><tbody class=""><tr class=""><th class=""><p>Vorname</p></th><th class=""><p>Nachname</p></th></tr><tr class=""><td class=""><p>Jerry</p></td><td class=""><p>Smith</p></td></tr><tr class=""><td class=""><p>Morty</p></td><td class=""><p>Smith</p></td></tr><tr class=""><td class=""><p>Rick</p></td><td class=""><p>Sanchez</p></td></tr></tbody></table>',
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", False],
            ["len:0/table/rows", 4],
            ["0/table/rows/0/cells/0/type", "header"],
            [
                "0/table/rows/0/cells/0/value",
                [
                    {"children": [{"text": "Vorname"}], "type": "p"},
                ],
            ],
            ["0/table/rows/0/cells/1/type", "header"],
            [
                "0/table/rows/0/cells/1/value",
                [
                    {"children": [{"text": "Nachname"}], "type": "p"},
                ],
            ],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [{"children": [{"text": "Jerry"}], "type": "p"}],
            ],
            ["0/table/rows/1/cells/1/type", "data"],
            [
                "0/table/rows/1/cells/1/value",
                [{"children": [{"text": "Smith"}], "type": "p"}],
            ],
            ["0/table/rows/2/cells/0/type", "data"],
            [
                "0/table/rows/2/cells/0/value",
                [{"children": [{"text": "Morty"}], "type": "p"}],
            ],
            ["0/table/rows/2/cells/1/type", "data"],
            [
                "0/table/rows/2/cells/1/value",
                [{"children": [{"text": "Smith"}], "type": "p"}],
            ],
            ["0/table/rows/3/cells/0/type", "data"],
            [
                "0/table/rows/3/cells/0/value",
                [{"children": [{"text": "Rick"}], "type": "p"}],
            ],
            ["0/table/rows/3/cells/1/type", "data"],
            [
                "0/table/rows/3/cells/1/value",
                [{"children": [{"text": "Sanchez"}], "type": "p"}],
            ],
        ],
    },
    "Table settings ui class": {
        "src": '<table class="ui table celled fixed striped very basic compact"><tbody class=""><tr class=""><th class=""><p>Vorname</p></th><th class=""><p>Nachname</p></th></tr><tr class=""><td class=""><p>Jerry</p></td><td class=""><p>Smith</p></td></tr><tr class=""><td class=""><p>Morty</p></td><td class=""><p>Smith</p></td></tr><tr class=""><td class=""><p>Rick</p></td><td class=""><p>Sanchez</p></td></tr></tbody></table>',
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", True],
            ["0/table/celled", True],
            ["0/table/compact", True],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", True],
            ["0/table/hideHeaders", False],
            ["len:0/table/rows", 4],
            ["0/table/rows/0/cells/0/type", "header"],
            [
                "0/table/rows/0/cells/0/value",
                [
                    {"children": [{"text": "Vorname"}], "type": "p"},
                ],
            ],
            ["0/table/rows/0/cells/1/type", "header"],
            [
                "0/table/rows/0/cells/1/value",
                [
                    {"children": [{"text": "Nachname"}], "type": "p"},
                ],
            ],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [{"children": [{"text": "Jerry"}], "type": "p"}],
            ],
            ["0/table/rows/1/cells/1/type", "data"],
            [
                "0/table/rows/1/cells/1/value",
                [{"children": [{"text": "Smith"}], "type": "p"}],
            ],
            ["0/table/rows/2/cells/0/type", "data"],
            [
                "0/table/rows/2/cells/0/value",
                [{"children": [{"text": "Morty"}], "type": "p"}],
            ],
            ["0/table/rows/2/cells/1/type", "data"],
            [
                "0/table/rows/2/cells/1/value",
                [{"children": [{"text": "Smith"}], "type": "p"}],
            ],
            ["0/table/rows/3/cells/0/type", "data"],
            [
                "0/table/rows/3/cells/0/value",
                [{"children": [{"text": "Rick"}], "type": "p"}],
            ],
            ["0/table/rows/3/cells/1/type", "data"],
            [
                "0/table/rows/3/cells/1/value",
                [{"children": [{"text": "Sanchez"}], "type": "p"}],
            ],
        ],
    },
    "Table simple": {
        "src": "<table><tr><td>A value</td></tr></table>",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            ["0/table/rows/1/cells/0/value", [{"text": "A value"}]],
        ],
    },
    "Table tbody": {
        "src": """<table class="plain">\n<tbody>\n<tr><td><b>Text1</b></td></tr>\n</tbody>\n</table>""",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [{"children": [{"text": "Text1"}], "type": "strong"}],
            ],
        ],
    },
    "Table text with link": {
        "src": '<table><tr><td>Plone <a href="https://plone.org">site</a></td></tr></table>',
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [
                    {"text": "Plone "},
                    {
                        "children": [{"text": "site"}],
                        "data": {
                            "target": None,
                            "title": None,
                            "url": "https://plone.org",
                        },
                        "type": "link",
                    },
                ],
            ],
        ],
    },
    "Table text with sup": {
        "src": "<table><tr><td>10<sup>2</sup></td></tr></table>",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            [
                "0/table/rows/1/cells/0/value",
                [{"text": "10"}, {"children": [{"text": "2"}], "type": "sup"}],
            ],
        ],
    },
    "Table text with thead": {
        "src": """<table class="plain"><thead>\n<tr><td><b>Heading</b></td></tr>\n</thead>\n</table>""",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", False],
            ["len:0/table/rows", 1],
            ["0/table/rows/0/cells/0/type", "header"],
            [
                "0/table/rows/0/cells/0/value",
                [{"children": [{"text": "Heading"}], "type": "strong"}],
            ],
        ],
    },
    "Table with whitespaces": {
        "src": "<table><tr><td>A value<br>&nbsp;</td></tr></table>",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", True],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [""]],
            ["0/table/rows/1/cells/0/type", "data"],
            ["0/table/rows/1/cells/0/value", [{"text": "A value\n "}]],
        ],
    },
    "Table with header": {
        "src": "<table><tr><th>Heading</th></tr><tr><td>A value</td></tr></table>",
        "tests": [
            ["0/@type", "slateTable"],
            ["0/table/basic", False],
            ["0/table/celled", True],
            ["0/table/compact", False],
            ["0/table/fixed", True],
            ["0/table/inverted", False],
            ["0/table/striped", False],
            ["0/table/hideHeaders", False],
            ["len:0/table/rows", 2],
            ["0/table/rows/0/cells/0/type", "header"],
            ["0/table/rows/0/cells/0/value", [{"text": "Heading"}]],
            ["0/table/rows/1/cells/0/type", "data"],
            ["0/table/rows/1/cells/0/value", [{"text": "A value"}]],
        ],
    },
}


@pytest.mark.parametrize(
    "name,src,path,expected",
    [[k, PARAMS[k]["src"], *v] for k in PARAMS for v in PARAMS[k]["tests"]],
)
def test_table_block(block_factory, traverse, name, src, path, expected):
    result = block_factory(src)
    if path == "":
        # Block is None
        assert result is expected
    else:
        value = traverse(result, path)
        assert value == expected, f"{name}: {value} != {expected}"

---
myst:
  html_meta:
    "description": "How to produce Plate content for Plone Aurora with collective.html2blocks, from HTML, from Markdown, or from existing Volto blocks."
    "property=og:description": "Produce Plate content for Plone Aurora with collective.html2blocks."
    "property=og:title": "Convert content to Plate | collective.html2blocks"
    "keywords": "Plone, Plone Aurora, collective.html2blocks, Plate, Slate, migration, guide"
---

# Convert content to Plate

This guide shows you how to produce content for the unified editor of {term}`Plone Aurora`.
Aurora keeps a whole page in one {term}`Plate` value, stored in a single block with the key `__somersault__`.
Every entry point uses the Slate converter unless you ask for Plate.
For what each node becomes, read {doc}`/reference/plate`.

## Convert HTML or Markdown in Python

Pass `converter="plate"` to `html_to_blocks()`, `markdown_to_blocks()` or `volto_blocks()`.

```python
from collective.html2blocks import converter

html = "<h1>Title</h1><p>Paragraph</p>"

result = converter.volto_blocks(html, converter="plate")
```

The result has the `__somersault__` block as its only block.

```python
{
    "blocks": {
        "__somersault__": {
            "@type": "__somersault__",
            "value": [
                {
                    "type": "h1",
                    "children": [{"text": "Title"}],
                    "blockWidth": "default",
                },
                {
                    "type": "p",
                    "children": [{"text": "Paragraph"}],
                    "blockWidth": "default",
                },
            ],
        }
    },
    "blocks_layout": {"items": []},
}
```

Aurora doesn't read `blocks_layout`, so its `items` list stays empty.

`html_to_blocks()` and `markdown_to_blocks()` return a list with that one block.

## Add the page title

A `title` block becomes a `title` node, and the text of that node is the title of the content.
Pass the block in `default_blocks`, and the text in `title`.

```python
html = "<p>Paragraph</p>"

result = converter.volto_blocks(
    html,
    default_blocks=[{"@type": "title"}],
    converter="plate",
    title="Welcome to Plone",
)
```

## Convert from the command line

Pass `--converter plate` to `convert`.
With `--title`, the page starts with a `title` node.

```shell
uv run html2blocks convert --converter plate --title "Welcome to Plone" input.html output.json
```

## Convert with the HTTP service

Send `"converter": "plate"` to `POST /html`, `POST /markdown` or `POST /volto`.

```json
{"html": "<p>Paragraph</p>", "converter": "plate"}
```

## Migrate existing Volto content

If your content already has Slate blocks, use `slate_to_plate()`.
It takes a content item with the `blocks` and `blocks_layout` keys, and it reads the text of a `title` block from the `title` key.

```python
from collective.html2blocks import converter

content = {
    "title": "Welcome to Plone",
    "blocks": {
        "a": {"@type": "title"},
        "b": {
            "@type": "slate",
            "value": [{"type": "p", "children": [{"text": "Paragraph"}]}],
        },
    },
    "blocks_layout": {"items": ["a", "b"]},
}

migrated = converter.slate_to_plate(content)
```

The `slate2plate` command does the same for a JSON file, and `POST /slate2plate` does it for a request body.

```shell
uv run html2blocks slate2plate page.json plate.json
```

The migration is additive and idempotent:

-   The original blocks and `blocks_layout` stay in the result, so you can compare them or go back.
-   A content item that already has the `__somersault__` block comes back unchanged.
-   A content item without `blocks`, or without a `blocks_layout` list, comes back unchanged.

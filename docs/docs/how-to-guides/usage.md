---
myst:
  html_meta:
    "description": "How to convert HTML and Markdown to Volto blocks in Python with collective.html2blocks, including layout, default blocks and additional blocks."
    "property=og:description": "Step-by-step guide to converting HTML and Markdown to Volto blocks from Python code."
    "property=og:title": "Convert HTML and Markdown in Python | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, Python, Volto, blocks, converter, HTML, Markdown, guide"
---

# Convert content in Python

This guide shows you how to convert HTML and Markdown to Volto blocks in your Python code.
Install the package first, as described in {doc}`/how-to-guides/installation`.

Import the converter module.

```python
from collective.html2blocks import converter
```

The functions in this module accept a string and return blocks.
For the full list of parameters, read the {doc}`/reference/api`.

## Convert to a list of blocks

Use `converter.html_to_blocks()` to convert an HTML string to a list of blocks.

```python
html = "<h1>Title</h1><p>Paragraph</p>"

blocks = converter.html_to_blocks(html)
```

Use `converter.markdown_to_blocks()` to convert a Markdown string to a list of blocks.

```python
markdown = "# Title\n\nParagraph"

blocks = converter.markdown_to_blocks(markdown)
```

## Convert to Volto blocks with layout

Use `converter.volto_blocks()` to get a dictionary with the `blocks` and `blocks_layout` keys.
Volto uses this structure to render a content item.

```python
html = "<h1>Title</h1><p>Paragraph</p>"

result = converter.volto_blocks(html)
print(result)
```

The output has this structure.
Each block identifier is a random UUID, so the identifiers differ on every run.

```python
{
    "blocks": {
        "835acd72-2184-443f-899b-202ffb1984f9": {
            "@type": "slate",
            "plaintext": "Title",
            "value": [{"type": "h1", "children": [{"text": "Title"}]}],
        },
        "b91949ab-b85d-4615-9327-3e7a1084fc51": {
            "@type": "slate",
            "plaintext": "Paragraph",
            "value": [{"type": "p", "children": [{"text": "Paragraph"}]}],
        },
    },
    "blocks_layout": {
        "items": [
            "835acd72-2184-443f-899b-202ffb1984f9",
            "b91949ab-b85d-4615-9327-3e7a1084fc51",
        ]
    },
}
```

To convert Markdown instead, pass `source_format="markdown"`.
The default is `"html"`.
Any other value raises a `ValueError`.

```python
markdown = "# Title\n\nParagraph"

result = converter.volto_blocks(markdown, source_format="markdown")
```

## Add blocks before or after the converted blocks

Pass `default_blocks` to place blocks before the converted blocks.
For example, add a `title` block so that the page title comes first.

```python
html = "<h1>Title</h1><p>Paragraph</p>"
default_blocks = [{"@type": "title"}]

result = converter.volto_blocks(html, default_blocks=default_blocks)
```

Pass `additional_blocks` to place blocks after the converted blocks.
Use keyword arguments for both parameters, because `additional_blocks` is the third positional parameter.

```python
html = "<h1>Title</h1><p>Paragraph</p>"
default_blocks = [{"@type": "title"}]
additional_blocks = [{"@type": "description"}]

result = converter.volto_blocks(
    html,
    default_blocks=default_blocks,
    additional_blocks=additional_blocks,
)
```

The `blocks_layout` list keeps the order: the default blocks come first, then the converted blocks, and then the additional blocks.

## Use the web service instead

If your migration runs in another language or in a separate process, call the HTTP service instead.
Read {doc}`/how-to-guides/run-http-service`.

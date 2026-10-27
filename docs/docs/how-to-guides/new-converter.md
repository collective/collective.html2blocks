---
myst:
  html_meta:
    "description": "How to implement and register a new block converter in collective.html2blocks."
    "property=og:description": "Guide to creating new block converters for collective.html2blocks."
    "property=og:title": "How to create a new block converter | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, block converter, Volto, migration, guide"
---

# Register a new converter

This guide shows you how to register a converter for an HTML element.
Use a block converter when the element must become a specific Volto block.
Use an element converter when the element becomes Slate content inside a block.

A block converter is a function that receives a BeautifulSoup element and returns a Volto block.
A Volto block is a dictionary with an `@type` key and the other properties that the Volto editor expects.
Register the function with the `@registry.block_converter` decorator.

An element converter returns Slate-compatible elements, such as paragraphs, headings, or inline formatting.
Those elements can be nested inside other blocks.
Register the function with the `@registry.element_converter` decorator.

## Create a block converter for the `code` element

This example converts a `<code>` element to a code block for `@plonegovbr/volto-code-block`.

```python
from bs4 import Tag
from collective.html2blocks import registry


@registry.block_converter("code")
def code_block_converter(element: Tag) -> dict:
    return {
        "@type": "codeBlock",
        "code": element.text,
        "language": "python",
        "lineNbr": 1,
        "showLineNumbers": False,
        "style": "dark",
        "wrapLongLines": True,
    }
```

The decorator registers the function as soon as Python imports the module.
Import the module before you call the converter, so that the registration takes effect.

## Check the registration

Run the `info` command to confirm that the converter is registered.

```shell
uv run html2blocks info
```

The new tag appears in the list of block converters.
For the decorator's full signature, read the {doc}`/reference/api`.

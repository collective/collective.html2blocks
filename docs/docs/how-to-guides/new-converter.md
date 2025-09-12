---
myst:
  html_meta:
    "description": "How to implement and register a new block converter in collective.html2blocks."
    "property=og:description": "Guide to creating new block converters for collective.html2blocks."
    "property=og:title": "How to create a new block converter | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, block converter, Volto, migration, guide"
---

# Registering a new converter

To implement a new block converter in `collective.html2blocks`, you typically register a function using the `@registry.block_converter` or `@registry.element_converter` decorator.

The `@registry.block_converter` decorator is used for functions that return a Volto block—an object with an `@type` key and other properties expected by Volto editors. These blocks are inserted directly into the output and can represent custom or third-party block types.

The `@registry.element_converter` decorator is used for functions that return internal Slate-compatible elements, such as paragraphs, headings, or inline formatting. These elements are further processed and may be nested within other blocks before being converted to Volto blocks if needed.

## A new block converter for the `<code>` element

This function receives a BeautifulSoup element and returns a dictionary in the Volto block format. For example, to handle the `<code>` element and produce a code block compatible with `@plonegovbr/volto-code-block`, you would define a converter that extracts the code content and returns the required JSON structure.

Here is a sample implementation for a `<code>` block converter:

```python
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
This converter will transform a `<code>` HTML element into a Volto code block, preserving the code content and formatting options. You can customize the converter to support other languages or block options as needed. Once registered, the converter will be used automatically during HTML-to-block conversion.

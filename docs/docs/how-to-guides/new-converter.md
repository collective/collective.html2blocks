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

## Create a block converter for the `aside` element

This example converts an `<aside>` element to a `callout` block, provided by a frontend add-on called `@example/volto-callout-block`.

```python
from bs4 import Tag
from collections.abc import Generator
from collective.html2blocks import registry
from dataclasses import dataclass


@dataclass(frozen=True)
class CalloutOptions:
    color: str = "blue"


@registry.block_converter(
    "aside",
    block_type="callout",
    package="@example/volto-callout-block",
    enabled=False,
    options=CalloutOptions,
    description="Callouts: <aside>.",
)
def callout_block(element: Tag) -> Generator[dict, None, None]:
    options: CalloutOptions = registry.block_options("callout")
    yield {"@type": "callout", "text": element.get_text(), "color": options.color}
```

A block converter is a generator: it yields one or more blocks.
The decorator registers the function as soon as Python imports the module.
Import the module before you call the converter, so that the registration takes effect.

The arguments after the tag names describe the block the converter produces:

`block_type`
:   The Volto `@type` of the block.
    It's the key that enables, disables and configures the block in the `blocks` setting.

`package`
:   The frontend package that provides the block.
    Use `@plone/volto` for the blocks of Volto core.

`enabled`
:   Whether the block is produced when no setting mentions it.
    Register blocks that come from an add-on with `enabled=False`, so that sites without the add-on keep their output.

`options`
:   A data class, decorated with `@dataclass`, with the options of the block and their defaults.
    The converter reads the options of the conversion in progress with `registry.block_options()`.

`description`
:   One line that says what the block is converted from.

`fallback`
:   A block converter to use while the block is disabled.
    Without one, the element is converted as if the block converter didn't exist.

Leave the arguments out to register a converter without a block type.
Such a converter is always used.

## Enable the block

The `callout` block is disabled by default, so enable it in the conversion.

```python
from collective.html2blocks.converter import html_to_blocks

blocks = html_to_blocks(
    "<aside>Read this first.</aside>",
    blocks={"callout": {"color": "red"}},
)
```

On the command line, use `--enable callout` and `--option callout.color=red`.

## Check the registration

Run the `blocks` command to confirm that the block type is registered.

```shell
uv run html2blocks blocks
```

The new block type appears with its package, its default state and its options.
The `info` command lists it too, along with the tag in the list of block converters.
For the decorator's full signature, read the {doc}`/reference/api`.

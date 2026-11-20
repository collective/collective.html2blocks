---
myst:
  html_meta:
    "description": "How collective.html2blocks converts Volto blocks and Slate nodes to the Plate value of Plone Aurora."
    "property=og:description": "The Slate to Plate conversion of collective.html2blocks."
    "property=og:title": "Plate output | collective.html2blocks"
    "keywords": "Plone, Plone Aurora, collective.html2blocks, Plate, Slate, main, __somersault__, reference"
---

# Plate output

The `plate` converter produces the `main` region of {term}`Plone Aurora`: a block with the key `main` in `blocks`.
The block has an `@type` and a `value`, and the `value` holds every node of the page, in order.
The conversion runs the Slate converter first, and then migrates its result, so the HTML is parsed the same way for both.

## Formats

The `plate_format` setting picks the key and the type of the block.
The `value` is the same in both formats.

| `plate_format` | Key in `blocks` | `@type` | For |
| --- | --- | --- | --- |
| `main` (default) | `main` | `plate` | Current Aurora sites. |
| `somersault` (deprecated) | `__somersault__` | `__somersault__` | Aurora sites that have not upgraded yet. Current sites read it as `main`. |

`slate_to_plate()` adds no block to a content item that already has a `main` or a `__somersault__` block, whatever the format.
The `slate` converter ignores the setting, but still rejects an unknown format.

`collective.html2blocks.utils.plate` provides the helpers behind the setting: `plate_block(value, plate_format)` wraps a value in the block, `body_key(plate_format)` returns its key, and `PLATE_FORMATS` lists the formats.

The migrations are ports of the ones Aurora applies at runtime.
The sections below also list what `collective.html2blocks` adds to them, because the Slate converter emits more than those migrations cover.

## Blocks

| Volto block | Plate node |
| --- | --- |
| `title` | A `title` node with the title of the content as its text. |
| Any block with a `value` list, such as `slate` | The nodes of the list. The other keys of the block, such as `plaintext`, are left out. |
| `slateTable` | A native `table` node, with `tr`, `th` and `td` children. |
| `codeBlock` | A native `code_block` node, with one `code_line` child per line and the language in `lang`. |
| Any other block | A `ploneBlock` node with the data of the block, a `blockWidth`, and an empty text child. |

Aurora drops a block that isn't registered in the site.
The converter can't see that registry, so it keeps every block as a `ploneBlock` node.
Aurora has no `slateTable` or `codeBlock` block, so these become native nodes instead.
A table with `hideHeaders` loses its first row, which is the hidden header, and the style options of the table are left out.

The `plate` converter enables `codeBlock`, so that fenced code keeps its lines and its language.
To turn this off, disable the block type.
A `<pre>` then goes through the Slate converter.

## Marks

Plate stores marks on the text nodes.

| Slate element | Plate mark |
| --- | --- |
| `strong` | `bold` |
| `em` | `italic` |
| `del`, `s` | `strikethrough` |
| `u` | `underline` |
| `sub` | `subscript` |
| `sup` | `superscript` |
| `code` | `code` |

## Links

A `link` node becomes an `a` node, and `data.url` and `data.target` become its `url` and `target`.
`data.title` is left out, like in Aurora.

## Lists

A `ul` or `ol` becomes paragraphs with the `indent` and `listStyleType` attributes.
`listStyleType` is `disc` or `decimal`.
The first item of an `ol` has `listRestartPolite`, and each following item of a list has `listStart`.

The `indent` of a nested list is its depth.
In a list item with several blocks, the first block carries the list marker, and the others only have the `indent`.

## Quotes

The text and the inline nodes of a `blockquote` are wrapped in paragraphs.

## Code

A `pre` node becomes a `code_block` node, with one `code_line` child per line.

## Block width

Each top-level native node gets a `blockWidth`.
A node without a valid width gets `default`.
The valid widths are `narrow`, `default`, `layout` and `full`.

## Nodes without a Plate equivalent

Other node types, such as the `dl`, `dt` and `dd` of a definition list, stay in the value as they are.
This is what Aurora does as well.

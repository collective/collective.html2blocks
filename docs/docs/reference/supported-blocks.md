---
myst:
  html_meta:
    "description": "The Volto block types collective.html2blocks can produce, the frontend packages that provide them, their default state and their options."
    "property=og:description": "Supported Volto block types in collective.html2blocks."
    "property=og:title": "Supported blocks | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, Volto, blocks, codeBlock, slateTable, reference"
---

# Supported blocks

`collective.html2blocks` converts HTML into the Volto block types below.
Each block type comes from a frontend package.
The site that receives the blocks must have that package installed, or the editor can't display the blocks.

The *Default* column says whether a block type is produced when no setting mentions it:

`on`
:   Produced by default. You can disable it.

`off`
:   Not produced unless you enable it. Blocks from add-ons are usually `off`.

`always`
:   Always produced. It can't be disabled. `slate` converts every element without a more specific block.

## Block types

```{include} _supported-blocks.md
```

## Enable, disable and configure blocks

Every entry point takes the same setting, keyed by the block type.
`true`, or a dictionary of options, enables a block type.
`false` disables it.
Block types left out keep their default state.

Python
:   Pass `blocks` to `html_to_blocks()`, `markdown_to_blocks()` or `volto_blocks()`.

    ```python
    from collective.html2blocks.converter import volto_blocks

    info = volto_blocks(
        source,
        blocks={"codeBlock": {"style": "light"}, "slateTable": False},
    )
    ```

Command line
:   Pass `--enable`, `--disable` and `--option` to `convert`.

    ```shell
    html2blocks convert --enable codeBlock --option codeBlock.style=light --disable slateTable page.md page.json
    ```

HTTP service
:   Send a `blocks` object to `POST /html`, `POST /markdown` or `POST /volto`.

    ```json
    {"html": "<pre>ls</pre>", "blocks": {"codeBlock": true}}
    ```

An unknown block type or option is an error, and so is a value of the wrong type.
The command line exits with status 2, and the HTTP service answers with status 400.

## Disabled blocks

The elements of a disabled block type are converted as if it didn't exist:

-   A `<pre>` with `codeBlock` disabled, and a `<table>` with `slateTable` disabled, become `slate` text.
-   An `<iframe>` whose provider block is disabled becomes an `iframe` block. With `iframe` disabled as well, it's dropped.
-   An `<img>` with `image` disabled, and a `<video>` with `video` disabled, are dropped.

## List the blocks of an installation

Add-ons can register more block types.
To list the block types of your installation, run the `blocks` command, or call `GET /blocks` on the HTTP service.

```shell
html2blocks blocks
html2blocks blocks --format json
```

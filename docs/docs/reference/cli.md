---
myst:
  html_meta:
    "description": "Reference for the html2blocks command line tool: the convert, info and server commands, their arguments, options and defaults."
    "property=og:description": "Reference for the collective.html2blocks command line tool."
    "property=og:title": "Command line reference | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, CLI, Typer, reference"
---

# Command line reference

The `html2blocks` command is installed with `collective.html2blocks`, but it needs an extra to run.
Install `collective.html2blocks[cli]` for the `convert` and `info` commands.
Install `collective.html2blocks[server]` for the `server` command.
The `all` extra installs both sets.
Run `html2blocks --help` to list the commands.
Run `html2blocks COMMAND --help` to see the options of a command.

## `convert`

Convert an HTML or Markdown file to a JSON file with Volto blocks.

Usage: `html2blocks convert [OPTIONS] SRC DST`

| Argument or option | Description | Default |
| --- | --- | --- |
| `SRC` | Path to the HTML or Markdown file to read. | Required |
| `DST` | Path of the JSON file to write. Its parent folder must exist. | Required |
| `--format` | Input format, `html` or `markdown`. | Detected from the suffix of `SRC` |
| `--enable BLOCK_TYPE` | Enable a block type, such as `codeBlock`. Repeat the option to enable more. | The default state of each block type |
| `--disable BLOCK_TYPE` | Disable a block type, such as `slateTable`. Repeat the option to disable more. | The default state of each block type |
| `--option BLOCK_TYPE.KEY=VALUE` | Set an option of a block type, such as `codeBlock.style=light`. The option also enables the block type. Repeat the option to set more. | The defaults of the block type |

The format is detected from the suffix of `SRC`.
Files with the `.md` or `.markdown` suffix are read as Markdown.
All other files are read as HTML.

If `SRC` does not exist, or if the parent folder of `DST` does not exist, the command prints a message and exits with status 1.

The block types, their default state and their options are listed in {doc}`/reference/supported-blocks`, and by the `blocks` command.
Boolean option values are `true`, `false`, `yes`, `no`, `on`, `off`, `1` or `0`.
An unknown block type or option, a value of the wrong type, or a block type both enabled and disabled makes the command print a message and exit with status 2.

The output is JSON, written with an indentation of two spaces.
It has the `blocks` and `blocks_layout` keys.

## `blocks`

List the Volto block types the converters can produce.
For each block type, the report gives the frontend package that provides it, its default state, what it's converted from, and its options with their defaults.

Usage: `html2blocks blocks [OPTIONS]`

| Option | Description | Default |
| --- | --- | --- |
| `--format` | Output format: `text`, `json` or `markdown`. | `text` |

The default state is `on`, `off`, or `always` for a block type that can't be disabled.

## `info`

Print the package name and version, followed by the block types with their package and default state, the block converters and the element converters that are registered.

Usage: `html2blocks info`

This command takes no options.

## `server`

Run the HTTP service with Uvicorn.

Usage: `html2blocks server [OPTIONS]`

| Option | Description | Default |
| --- | --- | --- |
| `--host` | Address to bind. | `127.0.0.1` |
| `--port` | Port to listen on. | `8000` |
| `--reload` / `--no-reload` | Restart the server when the source code changes. Use this option only during development. | `--no-reload` |

The endpoints of the service are described in the {doc}`/reference/http-service`.

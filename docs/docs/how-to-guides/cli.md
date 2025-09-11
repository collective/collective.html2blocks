---
myst:
  html_meta:
    "description": "How to use the {term}`CLI` for collective.html2blocks, including commands, options, and server endpoints."
    "property=og:description": "Guide to using the {term}`CLI` and block converters in collective.html2blocks."
    "property=og:title": "How to use the CLI | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, {term}`CLI`, {term}`Typer`, {term}`Uvicorn`, {term}`OpenAPI`, block converter, Volto, migration, guide"
---

# `html2blocks` command line application

Installing `collective.html2blocks` in your project will provide you with a new {term}`CLI` application named `html2blocks`.
To use it, either locate the Python virtual environment used by your project (usually present in the `.venv` folder of your backend codebase) and run `.venv/bin/html2blocks`, or if your project uses `uv` run `uv run html2blocks` and `uv` will correctly initiate this {term}`CLI` application.

All examples here will showcase `uv run html2blocks` for the sake of simplicity.

## The application

After running `uv run html2blocks` you will be granted with a list of options and commands available in the tool, powered by {term}`Typer`:

```text
Usage: html2blocks [OPTIONS] COMMAND [ARGS]...

 Main CLI callback for collective.html2blocks.

 This function is invoked when the CLI is run without a subcommand. It displays a welcome message and help information
 for available commands.
 Args:     ctx (typer.Context): Typer context object.
 Example::
 $ uv run html2blocks     Welcome to collective.html2blocks.

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                             │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.      │
│ --help                        Show this message and exit.                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ convert   Convert a HTML file to Volto blocks JSON.                                                                 │
│ info      Show information about the collective.html2blocks tool and its registrations.                             │
│ server    Run the HTML to Blocks API service.                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Commands

### `info`

This command displays information about the `collective.html2blocks` package and all converter {term}`Registration`.

```bash
uv run html2blocks info
```
will display:

```text
# collective.html2blocks - 1.0.0a0

## Block Converters
 - iframe: collective.html2blocks.blocks.iframe.iframe_block
 - img: collective.html2blocks.blocks.image.image_block
 - table: collective.html2blocks.blocks.table.table_block
 - video: collective.html2blocks.blocks.video.video_block
 - *: collective.html2blocks.blocks.slate.slate_block

## Element Converters
 - br: collective.html2blocks.blocks.slate.parser._br_
 - hr: collective.html2blocks.blocks.slate.parser._hr_
 - body: collective.html2blocks.blocks.slate.parser._body_
 - h1: collective.html2blocks.blocks.slate.parser._header_
 - h2: collective.html2blocks.blocks.slate.parser._header_
 - h3: collective.html2blocks.blocks.slate.parser._header_
 - h4: collective.html2blocks.blocks.slate.parser._header_
 - h5: collective.html2blocks.blocks.slate.parser._header_
 - h6: collective.html2blocks.blocks.slate.parser._header_
 - b: collective.html2blocks.blocks.slate.parser._strong_
 - strong: collective.html2blocks.blocks.slate.parser._strong_
 - code: collective.html2blocks.blocks.slate.parser._code_
 - div: collective.html2blocks.blocks.slate.parser._div_
 - pre: collective.html2blocks.blocks.slate.parser._pre_
 - a: collective.html2blocks.blocks.slate.parser._link_
 - span: collective.html2blocks.blocks.slate.parser._span_
 - blockquote: collective.html2blocks.blocks.slate.parser._block_
 - p: collective.html2blocks.blocks.slate.parser._block_
 - sub: collective.html2blocks.blocks.slate.parser._block_
 - sup: collective.html2blocks.blocks.slate.parser._block_
 - u: collective.html2blocks.blocks.slate.parser._block_
 - ol: collective.html2blocks.blocks.slate.parser._ol_
 - li: collective.html2blocks.blocks.slate.parser._block_
 - dt: collective.html2blocks.blocks.slate.parser._block_
 - dd: collective.html2blocks.blocks.slate.parser._block_
 - ul: collective.html2blocks.blocks.slate.parser._ul_
 - dl: collective.html2blocks.blocks.slate.parser._dl_
 - del: collective.html2blocks.blocks.slate.parser._s_
 - s: collective.html2blocks.blocks.slate.parser._s_
 - em: collective.html2blocks.blocks.slate.parser._em_
 - i: collective.html2blocks.blocks.slate.parser._em_
```
Of course, if in your project you did register additional converters, they should be displayed in here as well.

## `convert`
This command reads the HTML file at `SRC`, converts its contents to a JSON representing Volto block information (containing the `{term}`blocks` and `{term}`blocks_layout` keys) using the package's {term}`Converter`, and writes the result as JSON to `DST`.

Example usage, having a file named `input.html`:

```html
<div><p>Hello <strong>World!</strong></p></div>
```
you can run this command with:
```bash
uv run html2blocks convert input.html output.json
```

This will create a new file named `output.json` with the following contents:
```json
{
  "blocks": {
    "bc1eaf92-05f9-4dba-b28d-1996373f0076": {
      "@type": "slate",
      "plaintext": "Hello World!",
      "value": [
        {
          "type": "p",
          "children": [
            {
              "text": "Hello "
            },
            {
              "type": "strong",
              "children": [
                {
                  "text": "World!"
                }
              ]
            }
          ]
        }
      ]
    }
  },
  "blocks_layout": {
    "items": [
      "bc1eaf92-05f9-4dba-b28d-1996373f0076"
    ]
  }
}
```

## `server`

This command starts a {term}`Uvicorn` server hosting the FastAPI app for converting HTML to Volto blocks. You can customize the host, port, and enable reload for development.

| Option | Description | Default Value |
| --- | --- | --- |
| `--host` | Address to run the server | `127.0.0.1` |
| `--port` | Port number to be used | `8000` |
| `--reload` or `--no-reload` | Used during development, indicates if the server should look for changes in its codebase.  | `--no-reload` |
| `--help` | Show the help for the command | |

So, to run the server on a specific port, for example `8090`, you should run:

```bash
uv run html2blocks server --port 8090
```

and you should see:

```text
Starting HTML to Blocks service at http://127.0.0.1:8090
INFO:     Started server process [94408]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8090 (Press CTRL+C to quit)
```

The server provides an {term}`OpenAPI` documentation endpoint located at `http://<address>:<port>/docs` where you can check all available endpoints, and even try it out.

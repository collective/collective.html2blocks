---
myst:
  html_meta:
    "description": "How to convert HTML and Markdown files to Volto blocks JSON with the html2blocks command line tool."
    "property=og:description": "Guide to converting files from the collective.html2blocks command line."
    "property=og:title": "Convert files from the command line | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, CLI, Typer, Volto, blocks, converter, guide"
---

# Convert files from the command line

This guide shows you how to convert HTML and Markdown files to Volto blocks JSON with the `html2blocks` command.
For every option and default value, read the {doc}`/reference/cli`.

If your project uses uv, run the command with `uv run html2blocks`.
Otherwise, run `.venv/bin/html2blocks` from the virtual environment of your project.

## Convert a source file

Pass the source file and the destination JSON file to `convert`.

```shell
uv run html2blocks convert input.html output.json
```

The command writes the blocks and their layout to `output.json`.
The destination folder must already exist.

## Convert a Markdown file

The command reads files with a `.md` or `.markdown` suffix as Markdown.

```shell
uv run html2blocks convert input.md output.json
```

If your Markdown file has a different suffix, pass `--format markdown` to override the detection.

```shell
uv run html2blocks convert --format markdown notes.txt output.json
```

Use `--format html` to read a file with a Markdown suffix as HTML.

## Check the registered converters

To see which converters the command uses, run `info`.
It lists the block converters and the element converters that are registered.
If your project registers its own converters, they appear in this list.

```shell
uv run html2blocks info
```

To add a converter, read {doc}`/how-to-guides/new-converter`.

## Start the web service

The same command starts the HTTP service.
Read {doc}`/how-to-guides/run-http-service`.

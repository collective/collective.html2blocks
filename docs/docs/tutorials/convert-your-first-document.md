---
myst:
  html_meta:
    "description": "Tutorial: convert an HTML file and a Markdown file to Volto blocks, then call the collective.html2blocks HTTP service."
    "property=og:description": "Convert your first HTML and Markdown documents to Volto blocks with the html2blocks command and its HTTP service."
    "property=og:title": "Convert your first document | collective.html2blocks"
    "keywords": "Plone, Volto, blocks, collective.html2blocks, tutorial, HTML, Markdown, conversion"
---

# Convert your first document

In this tutorial, you convert an HTML file and a Markdown file to Volto blocks.
Then you send a Markdown string to the web service.
You need [uv](https://docs.astral.sh/uv/) and [Git](https://git-scm.com/) installed.

## Prepare the environment

First, clone the repository and install its dependencies.

```shell
git clone https://github.com/collective/collective.html2blocks.git
cd collective.html2blocks
make install
```

Next, check that the `html2blocks` command runs.

```shell
uv run html2blocks info
```

You should see the package name and its version, followed by two lists: the block converters and the element converters.

## Convert a source file

Now create a small HTML file in the repository folder.
Create a file named `example.html` with this content.

```html
<h1>Hello</h1>
<p>Your <strong>first</strong> document.</p>
```

Next, convert the file to JSON.

```shell
uv run html2blocks convert example.html example.json
```

You should see a message that starts with `Converted example.html contents into file`.
Open `example.json`.
The file has two keys: `blocks`, which holds the converted blocks, and `blocks_layout`, which lists the block identifiers in order.

## Convert a Markdown file

Markdown works the same way.
Create a file named `example.md` with this content.

```markdown
# Hello

Your **first** document.
```

The `.md` suffix tells the command to read the file as Markdown.
Convert it to JSON.

```shell
uv run html2blocks convert example.md example-markdown.json
```

Open `example-markdown.json`.
Its structure is the same as the structure of `example.json`.

## Call the web service

Next, start the HTTP service on port 8090.

```shell
uv run html2blocks server --port 8090
```

You should see the message `Starting HTML to Blocks service at http://127.0.0.1:8090`.
Keep the server running.
Open a second terminal in the same folder, and send a Markdown string to the service.

```shell
curl -X POST http://127.0.0.1:8090/markdown -H "Content-Type: application/json" -d '{"markdown": "# Hello"}'
```

The response is a JSON list that contains one `slate` block.
Return to the first terminal and stop the server by pressing {kbd}`Ctrl+C`.

## Next steps

You have now converted HTML and Markdown content with the command line and with the HTTP service.
To use the same conversion from your own Python code, read {doc}`/how-to-guides/usage`.
To see every option, read the {doc}`/reference/cli` and {doc}`/reference/http-service` pages.

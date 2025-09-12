---
myst:
  html_meta:
    "description": "Comprehensive guide to using collective.html2blocks: run the HTTP server, use the container image, and integrate as a Python dependency."
    "property=og:description": "Step-by-step instructions for running the HTML to Volto blocks service, using the CLI, Docker, and Python integration."
    "property=og:title": "Usage Guide | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, CLI, Docker, Python, Volto, blocks, converter, API, guide, usage"
---

# Usage

This guide provides step-by-step instructions for running the HTML to Volto blocks service, using the CLI, Docker, and Python integration.


## HTTP server

`collective.html2blocks` provides a simple HTTP server that can be used to convert HTML to Volto blocks.


### Container image

You can quickly deploy the HTML to Volto blocks service using our official container image, `ghcr.io/collective/html2blocks`. This method is ideal for testing, development, or integrating the service into containerized environments. To run the latest version and expose the service on port `8090` of your machine, use:

```bash
docker run -p 8090:8000 ghcr.io/collective/html2blocks:latest
```

To use a specific released version, simply replace `latest` with the desired version number. For example, to run version 1.0.0a1:

```bash
docker run -p 8090:8000 ghcr.io/collective/html2blocks:1.0.0a1
```


### `html2blocks` command line

If you have installed `collective.html2blocks` in your project or local Python virtual environment, you can start the HTTP server directly. This is useful for local development, integration, or running the service as part of a larger application. Run:

```bash
uv run html2blocks --port 8090
```

```{note}
For a full list of available options and advanced usage, see the [CLI documentation](./cli.md#server).
```


You can also run the latest published version of the server without installing the `collective.html2blocks` package locally. This is useful for quick tests or ephemeral environments.
Use the following command.

```bash
uvx html2blocks --from collective.html2blocks serve --port 8090
```

```{note}
This command only works with released versions of `collective.html2blocks`.
```


## Dependency to your code

After installing `collective.html2blocks` as a dependency (add it to your {file}`pyproject.toml`, {file}`setup.py`, {file}`setup.cfg`, or {file}`requirements.txt`), you can use its conversion features directly in your Python code. This is the recommended approach for programmatic HTML-to-blocks conversion and integration with other Python projects.

First, import the `converter` module in your Python code or interpreter:

```python
from collective.html2blocks import converter
```

You can then use one of the available functions.

### `converter.html_to_blocks`

Converts HTML to a list of Volto blocks, which you can further process or manipulate.

```python
html = "<h1>Title</h1><p>Paragraph</p>"

result = converter.html_to_blocks(html)
```


### `converter.volto_blocks`

Converts HTML to a dictionary containing both `blocks` and `blocks_layout` keys, suitable for direct use in Volto.
This function also supports prepending or appending blocks to the result for advanced layout control.

```python
html = "<h1>Title</h1><p>Paragraph</p>"

result = converter.volto_blocks(html)
print(result)
```

Will result in the following.

```python
{'blocks': {'835acd72-2184-443f-899b-202ffb1984f9': {'@type': 'slate', 'plaintext': 'Title', 'value': [{'type': 'h1', 'children': [{'text': 'Title'}]}]}, 'b91949ab-b85d-4615-9327-3e7a1084fc51': {'@type': 'slate', 'plaintext': 'Paragraph', 'value': [{'type': 'p', 'children': [{'text': 'Paragraph'}]}]}}, 'blocks_layout': {'items': ['835acd72-2184-443f-899b-202ffb1984f9', 'b91949ab-b85d-4615-9327-3e7a1084fc51']}}
```

To prepend a `title` block to the result, pass it as the `default_blocks` argument.

```python
html = "<h1>Title</h1><p>Paragraph</p>"
default_blocks = [{"@type": "title" }]
result = converter.volto_blocks(html, default_blocks=default_blocks)
print(result)
```

The foregoing code will prepend the title block to the list.

```python
{'blocks': {'99c40d97-56e0-488c-a34e-90190ed939c2': {'@type': 'title'}, '835acd72-2184-443f-899b-202ffb1984f9': {'@type': 'slate', 'plaintext': 'Title', 'value': [{'type': 'h1', 'children': [{'text': 'Title'}]}]}, 'b91949ab-b85d-4615-9327-3e7a1084fc51': {'@type': 'slate', 'plaintext': 'Paragraph', 'value': [{'type': 'p', 'children': [{'text': 'Paragraph'}]}]}}, 'blocks_layout': {'items': ['99c40d97-56e0-488c-a34e-90190ed939c2', '835acd72-2184-443f-899b-202ffb1984f9', 'b91949ab-b85d-4615-9327-3e7a1084fc51']}}
```

To append blocks to the result, use the `additional_blocks` parameter.

```python
html = "<h1>Title</h1><p>Paragraph</p>"
default_blocks = [{"@type": "title" }]
additional_blocks = [{"@type": "description" }]
result = converter.volto_blocks(html, default_blocks=default_blocks, additional_blocks)
print(result)
```

The foregoing code will result in the following.

```python
{'blocks': {'99c40d97-56e0-488c-a34e-90190ed939c2': {'@type': 'title'}, '835acd72-2184-443f-899b-202ffb1984f9': {'@type': 'slate', 'plaintext': 'Title', 'value': [{'type': 'h1', 'children': [{'text': 'Title'}]}]}, 'b91949ab-b85d-4615-9327-3e7a1084fc51': {'@type': 'slate', 'plaintext': 'Paragraph', 'value': [{'type': 'p', 'children': [{'text': 'Paragraph'}]}]}, 'd34b4273-d288-46c3-bd19-f3e7caea3c93': {'@type': 'title'}}, 'blocks_layout': {'items': ['99c40d97-56e0-488c-a34e-90190ed939c2', '835acd72-2184-443f-899b-202ffb1984f9', 'b91949ab-b85d-4615-9327-3e7a1084fc51', 'd34b4273-d288-46c3-bd19-f3e7caea3c93']}}
```

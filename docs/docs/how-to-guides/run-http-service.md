---
myst:
  html_meta:
    "description": "How to run the collective.html2blocks HTTP service with uv, uvx or the container image, and how to call its endpoints."
    "property=og:description": "Guide to running the HTML and Markdown to Volto blocks HTTP service."
    "property=og:title": "Run the HTTP service | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, HTTP, Docker, container, FastAPI, Volto, blocks, guide"
---

# Run the web service

This guide shows you how to run the HTTP service and how to convert content through it.
The request and response formats are listed in the {doc}`/reference/http-service`.

## Run the service from a project

If you installed `collective.html2blocks[server]` in your project, start the service with the `server` command.
The `server` extra provides the web framework and the server, so a plain `collective.html2blocks` install does not include it.

```shell
uv run html2blocks server --port 8090
```

The service listens on `127.0.0.1` by default.
To accept connections from other machines, or from a container, pass `--host 0.0.0.0`.

```shell
uv run html2blocks server --host 0.0.0.0 --port 8090
```

To run the latest released version without installing the package in your project, use `uvx`.
This command works only with released versions of the package.

```shell
uvx --from "collective.html2blocks[server]" html2blocks server --port 8090
```

## Run the container image

The official container image is `ghcr.io/collective/html2blocks`.
The service listens on port 8000 inside the container, so map that port to a port on your machine.

```shell
docker run -p 8090:8000 ghcr.io/collective/html2blocks:latest
```

To run a specific release, replace `latest` with the version number, for example `1.0.0a1`.

## Convert content

Send HTML to the `/html` endpoint to get a list of blocks.

```shell
curl -X POST http://127.0.0.1:8090/html -H "Content-Type: application/json" -d '{"html": "<p>Hello</p>"}'
```

Send Markdown to the `/markdown` endpoint, using the `markdown` field.

```shell
curl -X POST http://127.0.0.1:8090/markdown -H "Content-Type: application/json" -d '{"markdown": "# Hello"}'
```

Send content to the `/volto` endpoint to get the full structure with `blocks` and `blocks_layout`.
The field is always called `html`, even for Markdown.
Set `format` to `"markdown"` when the content is Markdown.

```shell
curl -X POST http://127.0.0.1:8090/volto -H "Content-Type: application/json" -d '{"html": "# Hello", "format": "markdown"}'
```

Omit `format`, or set it to `"html"`, when the content is HTML.

## Check that the service is running

Request the health endpoint.
It returns `{"status": "up"}` when the service is running.

```shell
curl http://127.0.0.1:8090/ok
```

The root endpoint, `/`, returns the service title, description and version.
The interactive API documentation is available at `/docs`.

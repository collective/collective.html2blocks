---
myst:
  html_meta:
    "description": "Reference for the collective.html2blocks HTTP service: endpoints, request bodies, responses and status codes."
    "property=og:description": "Endpoints, request fields and responses of the collective.html2blocks HTTP service."
    "property=og:title": "HTTP service reference | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, HTTP, REST, FastAPI, reference"
---

# Web service reference

The HTTP service is a FastAPI application.
Start it with the `server` command, as described in the {doc}`/reference/cli`.
The service needs the `server` extra: install `collective.html2blocks[server]`.
The interactive API documentation is available at `/docs`.

Every response includes the `X-Process-Time` header, which holds the processing time in seconds.

## Endpoints

| Method | Path | Request body | Response |
| --- | --- | --- | --- |
| `GET` | `/` | None | An object with the `title`, `description` and `version` keys. |
| `GET` | `/ok` | None | `{"status": "up"}` |
| `GET` | `/blocks` | None | A list with one object per supported block type. |
| `POST` | `/html` | `html`, `converter`, `title` and `blocks` | A list of blocks. |
| `POST` | `/markdown` | `markdown`, `converter`, `title` and `blocks` | A list of blocks. |
| `POST` | `/volto` | `html`, `format`, `default_blocks`, `additional_blocks`, `blocks`, `converter` and `title` | An object with the `blocks` and `blocks_layout` keys. |
| `POST` | `/slate2plate` | A content item with the `blocks` and `blocks_layout` keys | The content item with the `__somersault__` block. |

## `GET /blocks`

List the Volto block types the converters can produce.
Each object has the `block_type`, `package`, `description`, `enabled`, `required`, `tags`, `providers`, `options` and `fallback` keys.
`enabled` is the default state of the block type, and `required` is `true` for a block type that can't be disabled.
Each entry of `options` has the `name`, `type` and `default` keys.

## `POST /html`

Convert HTML to a list of blocks.

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `html` | string | Yes | None | The HTML to convert. |
| `converter` | string | No | `"slate"` | The converter to use, `"slate"` or `"plate"`. |
| `title` | string | No | `""` | The title of the content, for a `title` block with the `plate` converter. |
| `blocks` | object | No | `null` | Enables, disables and configures block types. See {ref}`http-service-blocks-field`. |

If `converter` has any other value, the service responds with status 400.

## `POST /markdown`

Convert Markdown to a list of blocks.

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `markdown` | string | Yes | None | The Markdown to convert. |
| `converter` | string | No | `"slate"` | The converter to use, `"slate"` or `"plate"`. |
| `title` | string | No | `""` | The title of the content, for a `title` block with the `plate` converter. |
| `blocks` | object | No | `null` | Enables, disables and configures block types. See {ref}`http-service-blocks-field`. |

If `converter` has any other value, the service responds with status 400.

## `POST /volto`

Convert HTML or Markdown to the structure that Volto uses for a content item.

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `html` | string | Yes | None | The HTML or Markdown to convert. The field has this name for both formats. |
| `format` | string | No | `"html"` | The format of `html`, either `"html"` or `"markdown"`. |
| `default_blocks` | list of objects | No | `null` | Blocks to place before the converted blocks. |
| `additional_blocks` | list of objects | No | `null` | Blocks to place after the converted blocks. |
| `blocks` | object | No | `null` | Enables, disables and configures block types. See {ref}`http-service-blocks-field`. |
| `converter` | string | No | `"slate"` | The converter to use, `"slate"` or `"plate"`. |
| `title` | string | No | `""` | The title of the content, for a `title` block in `default_blocks` or `additional_blocks` with the `plate` converter. |

If `format` has any other value, the service responds with status 422, the validation error status of FastAPI.
If `converter` has any other value, the service responds with status 400.

With the `plate` converter, the response has the `__somersault__` block as its only block.

## `POST /slate2plate`

Add the `__somersault__` block to a content item with Slate blocks.
The request body is the content item.

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `blocks` | object | Yes | None | The blocks of the content item. |
| `blocks_layout` | object | Yes | None | The layout of the blocks. |
| `title` | string | No | `""` | The title of the content item, for a `title` block. |

Other keys are returned unchanged.
The existing blocks stay in the response.
A content item that already has the `__somersault__` block comes back unchanged.
If `blocks` or `blocks_layout` is missing, the service responds with status 422.

(http-service-blocks-field)=

## The `blocks` field

The keys of `blocks` are Volto block types, as listed by `GET /blocks` and in {doc}`/reference/supported-blocks`.
`true`, or an object of options, enables a block type, and `false` disables it.
Block types left out keep their default state.

```json
{"html": "<pre>ls</pre>", "blocks": {"codeBlock": {"style": "light"}, "slateTable": false}}
```

For an unknown block type or option, a value of the wrong type, or a block type that can't be disabled, the service responds with status 400.
The `detail` key of the response says what is wrong.

## Example

Request:

```json
{"html": "# Hello", "format": "markdown"}
```

The response has the `blocks` and `blocks_layout` keys.
The block identifiers are random UUIDs.

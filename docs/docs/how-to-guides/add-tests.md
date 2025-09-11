---
myst:
  html_meta:
    "description": "How to add new tests to the collective.html2blocks codebase, including test parametrization and traversal fixture usage."
    "property=og:description": "How to guide for adding and structuring tests in collective.html2blocks."
    "property=og:title": "How to add tests | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, testing, pytest, traversal, parametrization, guide"
---


# Adding tests

This guide explains how to add new tests to the `collective.html2blocks` codebase, covering test parametrization, the use of the `traverse` fixture, and the organization of test cases for converters and API endpoints. The codebase uses {term}`pytest` and YAML-based parametrization for flexible, maintainable testing.

## Introduction: Test parametrization and the `traverse` fixture

Tests in `collective.html2blocks` are parametrized using YAML files, which define input data and expected results. The `traverse` fixture is a utility that allows you to extract and assert values from deeply nested dictionaries and lists using a path-like syntax. You can also apply simple functions (like `len`, `type`, or `keys`) to the traversed value by appending a colon and function name, for example `foo/bar:baz:len`. This makes it easy to write concise, readable assertions in your test cases.

## Testing the converter

This section covers how to test the main converter functions, such as `collective.html2blocks.converter.html_to_blocks` and `collective.html2blocks.converter.volto_blocks`. These functions are responsible for transforming HTML input into Volto blocks or internal representations. Tests should verify that the conversion logic produces the expected block structures for a variety of input scenarios.


### `html_to_blocks` function

To add a test for `html_to_blocks`, edit `tests/_data/test_html_to_blocks.yml` and add a new entry under `params`:

```yaml
params:
  - name: div with one paragraph
    src: <div><p>Hello World!</p></div>
    tests:
      - path: "len:"
        expected: 1
      - path: "0/@type"
        expected: slate
      - path: "0/plaintext"
        expected: Hello World!
      - path: "len:0/value"
        expected: 1
      - path: "0/value/0/type"
        expected: p
      - path: "0/value/0/children/0/text"
        expected: Hello World!
```


### `volto_blocks` function

To add a test for `volto_blocks`, edit `tests/_data/test_volto_blocks.yml` and add a new entry:

```yaml
params:
  - name: Simple Case
    src: |
      <div><p>Hello</p> <p>World!</p></div>
    default_blocks: [{"@type": "title"}, {"@type": "description"}]
    tests:
      - path: "len:blocks"
        expected: 5
      - path: "len:blocks_layout/items"
        expected: 5
```

## Testing the http-based API

This section describes how to test the FastAPI endpoints provided by `collective.html2blocks`. These endpoints expose conversion logic over HTTP, allowing integration with external tools and migration workflows.


### `/html` endpoint

To add a test for the `/html` endpoint, edit `tests/_data/test_services_html.yml` and add a new entry:

```yaml
params:
  - name: Simple Case
    src: |
      <div><p>Hello World!</p></div>
    converter: slate
    tests:
      - path: "len:"
        expected: 1
      - path: "0/@type"
        expected: "slate"
      - path: "0/plaintext"
        expected: "Hello World!"
      - path: "len:0/value"
        expected: 1
      - path: "0/value/0/type"
        expected: "p"
      - path: "0/value/0/children/0/text"
        expected: "Hello World!"
```


### `/volto` endpoint

To add a test for the `/volto` endpoint, edit `tests/_data/test_services_volto.yml` and add a new entry:

```yaml
params:
  - name: Simple Case
    src: |
      <div><p>Hello</p> <p>World!</p></div>
    default_blocks: [{"@type": "title"}, {"@type": "description"}]
    additional_blocks: []
    tests:
      - path: "len:blocks"
        expected: 5
      - path: "len:blocks_layout/items"
        expected: 5
```

## Testing blocks converters

This section explains how to test individual block converters, such as those for iframe, image, slate, and table blocks. Each converter should be tested with representative input and expected output, using YAML files for parametrization and the `traverse` fixture for assertions.


### iframe

To add a test for the iframe block converter, edit `tests/_data/test_iframe_block.yml` and add a new entry:

```yaml
params:
  - name: soundcloud
    src: '<iframe width="480" hfor examplet="270" src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/1275507478&amp;color=%23ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;show_reposts=false&amp;show_teaser=true&amp;visual=true" allowfullscreen></iframe>'
    tests:
      - path: "0/@type"
        expected: 'soundcloudBlock'
      - path: "0/soundcloudId"
        expected: '1275507478'
```


### image

To add a test for the image block converter, edit `tests/_data/test_image_block.yml` and add a new entry:

```yaml
params:
  - name: Image without scale
    src: '<img src="https://plone.org/news/item/@@images/44ae2493-53fb-4221-98dc-98fa38d6851a.jpeg" title="A Picture" alt="Picture of a person" class="image-right">'
    tests:
      - path: "0/@type"
        expected: 'image'
      - path: "0/url"
        expected: https://plone.org/news/item
      - path: "0/title"
        expected: "A Picture"
      - path: "0/alt"
        expected: "Picture of a person"
      - path: "0/size"
        expected: "m"
      - path: "0/align"
        expected: "right"
```


### slate

To add a test for the slate block converter, edit `tests/_data/test_slate_block.yml` and add a new entry:

```yaml
params:
  - name: Simple paragraph
    src: <p>Hello World!</p>
    tests:
      - path: "0/@type"
        expected: 'slate'
      - path: "0/plaintext"
        expected: 'Hello World!'
      - path: "0/value/0/type"
        expected: 'p'
      - path: "0/value/0/children/0/text"
        expected: 'Hello World!'
```


### table

To add a test for the table block converter, edit `tests/_data/test_table_block.yml` and add a new entry:

```yaml
params:
  - name: Table with br
    src: '<table class="plain"><tbody><tr><td><br/>Text</td></tr></tbody></table>'
    tests:
      - path: "0/@type"
        expected: "slateTable"
      - path: "0/table/basic"
        expected: False
      - path: "0/table/celled"
        expected: True
      - path: "0/table/compact"
        expected: False
      - path: "0/table/fixed"
        expected: True
      - path: "0/table/hideHeaders"
        expected: True
      - path: "0/table/inverted"
        expected: False
      - path: "len:0/table/rows"
        expected: 2
      - path: "0/table/rows/0/cells/0/type"
        expected: "header"
      - path: "0/table/rows/0/cells/0/value"
        expected: ['']
      - path: "0/table/rows/1/cells/0/type"
        expected: "data"
      - path: "0/table/rows/1/cells/0/value"
        expected: [{'text': "\nText"}]
```

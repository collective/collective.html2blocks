# Agent guidelines for collective.html2blocks

## Tests

Tests are data first.
A new case goes in a YAML fixture in `tests/_data/`, not in a Python test.
Before you add a test, read the fixture and the test function next to the code you changed.
The full guide is in `docs/docs/how-to-guides/add-tests.md`.

Run the suite with `make test`.
Run `make format` and `make lint` before you commit.

### How fixtures work

`pytest_generate_tests` in `tests/conftest.py` matches a test function to the fixture with the same name: `test_html_to_blocks` reads `tests/_data/test_html_to_blocks.yml`.
There's no registration step, so a renamed file or function stops parametrizing the test without an error.

```yaml
---
setup:
  argnames: ["name", "src", "path", "expected"]
  test_args: ["path", "expected"]
params:
  - name: Nested marks
    src: <p><strong><em>both</em></strong></p>
    tests:
      - path: "0/children"
        expected: [{text: both, bold: true, italic: true}]
```

-   `argnames` must match the parameters of the test function, by name.
-   Names in `test_args` come from each entry of `tests`. All the others come from the entry in `params`.
-   Every entry in `params` must have every one of the other names.
-   Each `path` entry is one test. To check a change, compare the suite total with the previous total plus the `path` entries you added.

### Paths

The `traverse` fixture reads the value at `path`:

-   `/` separates keys and list indexes: `0/value/0/type`.
-   A prefix with a colon applies a function to the value at that path: `len:0/value`, `keys:0`, `type:0`.
-   `len:` alone is the length of the root.

Prefer a whole node as `expected` when the shape matters, because it also fails on extra keys.

### Which fixture

| You changed | Fixture | Test |
| --- | --- | --- |
| HTML to Slate | `test_html_to_blocks.yml`, `test_slate_block.yml` | `tests/converter/`, `tests/blocks/slate/` |
| A block converter | `test_image_block.yml`, `test_iframe_block.yml`, `test_table_block.yml` | `tests/blocks/` |
| `volto_blocks()` | `test_volto_blocks.yml` | `tests/converter/` |
| HTML to Plate | `test_html_to_plate.yml` | `tests/converter/test_converter_plate.py` |
| Markdown to Plate | `test_markdown_to_plate.yml` | `tests/converter/test_converter_plate.py` |
| `volto_blocks()` with Plate | `test_volto_blocks_plate.yml` | `tests/converter/test_converter_plate.py` |
| Slate values that the converter doesn't produce | `test_migrate_value.yml` | `tests/utils/test_utils_plate.py` |
| A single Volto block to Plate nodes | `test_nodes_from_block.yml` | `tests/utils/test_utils_plate.py` |
| A content item to Plate | `test_migrate_content.yml` | `tests/utils/test_utils_plate.py` |
| HTTP endpoints | `test_services_html.yml`, `test_services_volto.yml`, `test_services_volto_plate.yml`, `test_services_slate2plate.yml` | `tests/services/` |

Add the sources of a new behavior to a Slate fixture, too.
`test_fixture_sources_to_plate` runs every source of the Slate fixtures through the `plate` converter, so a new Slate case also checks the Plate output.
If you add a Slate fixture, add it to `FIXTURES` in `tests/converter/test_converter_plate.py`.

### When Python is the right place

Write a plain test only for what a `path` and an `expected` value can't express:

-   Error paths, status codes and exit codes.
-   Default behavior, such as `slate` staying the default converter.
-   Properties of a result, such as idempotency or an input left unchanged.
-   Command line tests, in `tests/cli/`, which work with files.

Keep these short, and use `@pytest.mark.parametrize` for repeated cases.

### Behavior changes

A green suite doesn't prove a behavior change.
Add a test for the new behavior, confirm that it fails without the change, and cover what the change must not do.

Before you refactor a converter, save the output of `html_to_blocks` for every fixture source, and compare it after the refactor.
The default `slate` output must not change by accident.

Table rows and cells have random `key` values.
Use the `strip_keys` fixture to compare converted tables.

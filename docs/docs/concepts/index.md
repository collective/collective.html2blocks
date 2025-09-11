---
myst:
  html_meta:
    "description": "Key concepts behind collective.html2blocks, including Volto blocks, migration, extensibility, and editor support."
    "property=og:description": "Concepts and architectural principles of collective.html2blocks for Plone and Volto."
    "property=og:title": "Concepts | collective.html2blocks documentation"
    "keywords": "Plone, Volto, blocks, migration, Slate, volto-slate, extensibility, concepts"
---

# Concepts

{term}`Plone` traditionally stored rich-text content as HTML. With the introduction of {term}`Volto`, content is now structured as {term}`blocks`(JSON objects that define page layout and content for the Volto frontend). This shift enables a more flexible, component-based editing experience, but also requires new tools for migrating legacy content.

## Migration and Extensibility

Earlier, the Plone community used the [Blocks Conversion Tool](https://github.com/plone/blocks-conversion-tool) to convert HTML to Volto blocks during migrations. While effective, it lacked extensibility and only offered an HTTP interface.

`collective.html2blocks` was designed to address these limitations by:

- Allowing developers to register new converters for HTML elements, making it easy to adapt or extend block conversion for custom needs.
- Providing direct Python APIs for integration with migration frameworks such as {term}`collective.exportimport`, {term}`Transmogrifier`, or {term}`collective.transmute`.
- Emphasizing type annotations and comprehensive test coverage for reliability and maintainability.

## Editor Support: Volto-Slate

Although support for DraftJS (the previous default block editor for Volto) is technically possible, collective.html2blocks focuses on {term}`volto-slate`, the default rich-text editor since Volto 16. {term}`volto-slate` is built on top of {term}`Slate`, providing advanced {term}`WYSIWYG` capabilities for content editing in Plone.

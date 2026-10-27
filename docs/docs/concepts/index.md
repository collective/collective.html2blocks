---
myst:
  html_meta:
    "description": "Key concepts behind collective.html2blocks, including Volto blocks, migration, extensibility, input formats and editor support."
    "property=og:description": "Concepts and architectural principles of collective.html2blocks for Plone and Volto."
    "property=og:title": "Concepts | collective.html2blocks documentation"
    "keywords": "Plone, Volto, blocks, migration, Slate, volto-slate, extensibility, HTML, Markdown, concepts"
---

# Concepts

{term}`Plone` traditionally stored rich-text content as HTML.
With the introduction of {term}`Volto`, content is structured as {term}`blocks`.
A block is a JSON object that defines the layout and content of part of a page in the Volto frontend.
This shift enables a more flexible, component-based editing experience.
It also requires new tools to migrate legacy content.

## Migration and extensibility

Earlier, the Plone community used the [Blocks Conversion Tool](https://github.com/plone/blocks-conversion-tool) to convert HTML to Volto blocks during migrations.
That tool offered only an HTTP interface and was hard to extend.

`collective.html2blocks` addresses these limitations in three ways:

- You can register new converters for HTML elements, so you can adapt the conversion to your content.
- You can call the conversion from Python, which makes it easy to use in migration frameworks such as {term}`collective.exportimport`, {term}`Transmogrifier`, or {term}`collective.transmute`.
- The code uses type annotations and has broad test coverage.

## Input formats

HTML is the main input format.
The package parses the HTML and converts each block-level element with a registered block converter.
Elements without a specific converter fall back to the {term}`Slate` converter.

The package also accepts Markdown.
It renders the Markdown to HTML first, using the CommonMark rules with tables and strikethrough enabled.
Then it runs the rendered HTML through the same converters as any HTML input.

Because of this design, a Markdown document produces the same blocks as its HTML rendering.
You maintain one set of converters for both formats.
Markdown is convenient for authors who write content by hand, while HTML is what legacy sites usually store.

## Editor support

Although support for DraftJS, the previous default block editor for Volto, is technically possible, `collective.html2blocks` focuses on {term}`volto-slate`.
{term}`volto-slate` has been the default rich-text editor since Volto 16.
It is built on top of {term}`Slate`, and it provides advanced {term}`WYSIWYG` capabilities for content editing in Plone.

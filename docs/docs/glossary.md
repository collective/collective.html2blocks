---
myst:
  html_meta:
    "description": "Terms and definitions used throughout the Plone Sphinx Theme documentation."
    "property=og:description": "Terms and definitions used throughout the Plone Sphinx Theme documentation."
    "property=og:title": "Glossary"
    "keywords": "Plone, documentation, glossary, term, definition"
---

This glossary provides example terms and definitions relevant to **collective.html2blocks**.
Technical documentation for the collective.html2blocks package

```{note}
This is an example glossary demonstrating MyST Markdown’s `{glossary}` directive. You can adapt it for your project’s appendix by editing or replacing these entries with your own terms and definitions.
```

(glossary-label)=

# Glossary

```{glossary}
:sorted: true

Plone
    [Plone](https://plone.org/) is an open-source content management system that is used to create, edit, and manage digital content, like websites, intranets and custom solutions.
    It comes with over 20 years of growth, optimisations, and refinements.
    The result is a system trusted by governments, universities, businesses, and other organisations all over the world.

add-on
    An add-on in Plone extends its functionality.
    It is code that is released as a package to make it easier to install.

    In Volto, an add-on is a JavaScript package.

    In Plone core, an add-on is a Python package.

    -   [Plone core add-ons](https://github.com/collective/awesome-plone#readme)
    -   [Volto add-ons](https://github.com/collective/awesome-volto#readme)
    -   [Add-ons tagged with the trove classifier `Framework :: Plone` on PyPI](https://pypi.org/search/?c=Framework+%3A%3A+Plone)

Plone Sphinx Theme
plone-sphinx-theme
    [Plone Sphinx Theme](https://plone-sphinx-theme.readthedocs.io/) is a Sphinx theme for [Plone 6 Documentation](https://6.docs.plone.org/), [Plone Conference Training](https://training.plone.org/), and documentation of various Plone packages.
    This scaffold uses Plone Sphinx Theme.

Markedly Structured Text
MyST
    [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/) is a rich and extensible flavor of Markdown, for authoring Plone Documentation.
    The sample documentation in this scaffold is written in MyST.

Sphinx
    [Sphinx](https://www.sphinx-doc.org/en/master/) is a tool that makes it easy to create intelligent and beautiful documentation.
    It was originally created for Python documentation, and it has excellent facilities for the documentation of software projects in a range of languages.
    It can generate multiple output formats, including HTML and PDF, from a single source.
    This scaffold uses Sphinx to generate documentation in HTML format.

blocks
    Blocks are the fundamental components of a page layout in {term}`Volto`.

Slate
    [Slate.js](https://docs.slatejs.org/) is a highly customizable platform for creating rich-text editors, also known as {term}`WYSIWYG` editors.
    It enables you to create powerful, intuitive editors similar to those you've probably used in Medium, Dropbox Paper, or Google Docs.

`volto-slate`
    `volto-slate` is an interactive default text editor for Volto, developed on top of {term}`Slate`, offering enhanced {term}`WYSIWYG` functionality and behavior.

Volto
    [Volto](https://github.com/plone/volto) is a React-based frontend for Plone.

CMS
    Content Management System

REST
    REST stands for [Representational State Transfer](https://en.wikipedia.org/wiki/Representational_state_transfer). It is a software architectural principle to create loosely coupled web APIs.

Transmogrifier
    [Transmogrifier](https://github.com/collective/collective.transmogrifier) provides support for building pipelines that turn one thing into another. Specifically, transmogrifier pipelines are used to convert and import legacy content into a Plone site. It provides the tools to construct pipelines from multiple sections, where each section processes the data flowing through the pipe.

collective.exportimport
    [collective.exportimport](https://github.com/collective/collective.exportimport) is a package to export and import content, members, relations, translations, localroles and much more.

collective.transmute
    [collective.transmute](https://github.com/collective/collective.transmute) is a package to convert data from collective.exportimport to plone.exportimport

pytest
    [pytest](https://docs.pytest.org/) is a Python test framework that makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.

```

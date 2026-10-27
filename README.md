<h1 align="center">collective.html2blocks</h1>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/collective.html2blocks)](https://pypi.org/project/collective.html2blocks/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.html2blocks)](https://pypi.org/project/collective.html2blocks/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/collective.html2blocks)](https://pypi.org/project/collective.html2blocks/)
[![PyPI - License](https://img.shields.io/pypi/l/collective.html2blocks)](https://pypi.org/project/collective.html2blocks/)
[![PyPI - Status](https://img.shields.io/pypi/status/collective.html2blocks)](https://pypi.org/project/collective.html2blocks/)


[![CI](https://github.com/collective/collective.html2blocks/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective.html2blocks/actions/workflows/main.yml)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective.html2blocks)](https://github.com/collective/collective.html2blocks)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective.html2blocks?style=social)](https://github.com/collective/collective.html2blocks)

</div>

**collective.html2blocks** helps with migrations from old Plone versions -- and other CMS -- to Volto.
It converts HTML and Markdown content into Volto blocks.

## Installation

Install the converter as a library with `pip install collective.html2blocks`.
It needs only the converter's own dependencies.

To use the `html2blocks` command, install the `cli` extra: `pip install "collective.html2blocks[cli]"`.
To run the HTTP service, install the `server` extra: `pip install "collective.html2blocks[server]"`.
The `all` extra installs both.

Read the [documentation](https://collective.github.io/collective.html2blocks).

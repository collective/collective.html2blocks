---
myst:
  html_meta:
    "description": "How to install collective.html2blocks: supported methods, dependency management, and integration with Python projects."
    "property=og:description": "Step-by-step guide to installing collective.html2blocks using pyproject.toml, setup.py, or requirements.txt."
    "property=og:title": "Installation Guide | collective.html2blocks"
    "keywords": "Plone, collective.html2blocks, installation, Python, dependency, pyproject.toml, setup.py, requirements.txt, guide"
---

# Install collective.html2blocks

This guide shows you how to add `collective.html2blocks` to your Python project.
The package requires Python 3.12 or later.
Choose the method that matches your project.

1.  `pyproject.toml`

    Use this method for modern Python projects.
    Add `collective.html2blocks` to the `dependencies` list in your {file}`pyproject.toml` file.
    This approach works with build tools such as {term}`uv`, Poetry, or any other {term}`PEP 621`-compliant tool.

    ```toml
    [project]
    dependencies = [
        "collective.html2blocks",
    ]
    ```

1.  `setup.py`

    Use this method for traditional {term}`setuptools` projects.
    Add `collective.html2blocks` to the `install_requires` list in your {file}`setup.py` file.

    ```python
    setup(
        # ...
        install_requires=[
            "collective.html2blocks",
        ],
    )
    ```

1.  `requirements.txt`

    Use this method if your project manages dependencies with pip.
    Add `collective.html2blocks` to your {file}`requirements.txt` file.

    ```text
    collective.html2blocks
    ```

## Reinstall with updated dependencies

After you change your dependency file, run your project's installation command again.
For example, run `pip install -r requirements.txt` or `uv sync`, or use the equivalent command of your build tool.

To learn how to write version constraints, read the [Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/) specification.

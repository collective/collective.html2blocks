---
myst:
    html_meta:
        "description": "How to install collective.html2blocks: supported methods, dependency management, and integration with Python projects."
        "property=og:description": "Step-by-step guide to installing collective.html2blocks using pyproject.toml, setup.py, or requirements.txt."
        "property=og:title": "Installation Guide | collective.html2blocks"
        "keywords": "Plone, collective.html2blocks, installation, Python, dependency, pyproject.toml, setup.py, requirements.txt, guide"
---

# Installation

You can install `collective.html2blocks` in your project using several supported methods, depending on your project's setup and preferred workflow.


1.  `pyproject.toml`

    This method is recommended for modern Python projects.
    
    Add `collective.html2blocks` to the `dependencies` section of your {file}`pyproject.toml` file. This approach works with build tools like {term}`uv`, Poetry or other {term}`PEP 621`-compliant projects.
    
    ```toml
    [project]
    dependencies = [
        "collective.html2blocks",
    ]
    ```


1.  `setup.py`

    This method is for traditional setuptools projects.
    
    Add `collective.html2blocks` to the `install_requires` list in your {file}`setup.py` file. This is common for legacy or projects based on {term}`setuptools`.
    
    ```python
    install_requires=[
        "collective.html2blocks"
    ],
    ```


1.  `requirements.txt`

    This method uses direct requirements management.
    
    Add `collective.html2blocks` to your {file}`requirements.txt` file. This is the simplest method for projects that use pip for dependency management.
    
    ```txt
    collective.html2blocks
    ```

## Reinstall with updated dependencies

After updating your dependency file, re-run your project's installation command (for example, `pip install -r requirements.txt`, `uv sync`, or your build tool's equivalent). The package will be installed and available for use in your environment.

Refer to the official [Dependency specifiers](https://packaging.python.org/en/latest/specifications/dependency-specifiers/) documentation for details on specifying versions and advanced dependency options.

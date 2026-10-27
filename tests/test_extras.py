"""
Check that the converter works without the ``cli`` and ``server`` extras.

Each check runs in a new interpreter where the modules provided by the extras
are blocked, so a library module that imports one of them fails the test.
"""

from pathlib import Path

import subprocess
import sys
import textwrap


EXTRA_MODULES = ("typer", "fastapi", "uvicorn", "starlette")


def _run(code: str) -> subprocess.CompletedProcess:
    """
    Run a Python snippet in a new interpreter with the extras blocked.

    :param code: Python source to run after the extra modules are blocked.
    :returns: The completed process, with captured stdout and stderr.
    """
    blocked = "\n".join(f"sys.modules[{name!r}] = None" for name in EXTRA_MODULES)
    source = f"import sys\n{blocked}\n{textwrap.dedent(code)}"
    # The interpreter is the test's own, and the snippet is fixed test source.
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", source],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).parent,
    )


def test_converter_works_without_extras():
    """The converter imports and converts Markdown when no extra is installed."""
    result = _run(
        """
        import collective.html2blocks
        import collective.html2blocks.converter as converter

        blocks = converter.markdown_to_blocks("# hi")
        print(len(blocks))
        """
    )
    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) > 0


def test_package_metadata_available_without_extras():
    """The package version and private types import without the extras."""
    result = _run(
        """
        from collective.html2blocks import __version__
        from collective.html2blocks import _types

        print(__version__)
        """
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()

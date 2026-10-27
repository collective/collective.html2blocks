"""
Check the message printed when an extra needed by the ``html2blocks`` command is missing.

The missing package is simulated by setting its entry in ``sys.modules`` to ``None``
inside a new interpreter, so the import fails the same way it does in a real
environment without the extra.
"""

from pathlib import Path

import pytest
import subprocess
import sys
import textwrap


def _run_cli(blocked: tuple[str, ...], argv: list[str]) -> subprocess.CompletedProcess:
    """
    Run the ``html2blocks`` entry point in a new interpreter with modules blocked.

    :param blocked: Module names to block, so their import fails.
    :param argv: Arguments passed to the command, after the program name.
    :returns: The completed process, with captured stdout and stderr.
    """
    lines = [f"sys.modules[{name!r}] = None" for name in blocked]
    source = textwrap.dedent(
        """
        import sys
        {blocked}
        sys.argv = ["html2blocks", *{argv!r}]
        from collective.html2blocks.cli import cli
        cli()
        """
    ).format(blocked="\n".join(lines), argv=argv)
    # The interpreter is the test's own, and the snippet is fixed test source.
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", source],
        capture_output=True,
        text=True,
        check=False,
        cwd=Path(__file__).parent,
    )


def test_missing_typer_prints_extra_hint_and_exits_1():
    """Without typer, the command prints one line naming the cli extra and exits 1."""
    result = _run_cli(("typer",), ["info"])
    assert result.returncode == 1
    assert "typer is not installed" in result.stderr
    assert 'pip install "collective.html2blocks[cli]"' in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("missing", ["fastapi", "uvicorn"])
def test_missing_server_dependency_prints_extra_hint_and_exits_1(missing):
    """Without fastapi or uvicorn, ``server`` names the server extra and exits 1."""
    result = _run_cli((missing,), ["server"])
    assert result.returncode == 1
    assert f"{missing} is not installed" in result.stderr
    assert 'pip install "collective.html2blocks[server]"' in result.stderr
    assert "Traceback" not in result.stderr

"""
Report optional dependencies that are not installed.

The converter needs only the base dependencies. The ``html2blocks`` command needs
the ``cli`` extra, and the HTTP service needs the ``server`` extra.
"""

from typing import NoReturn

import sys


def exit_missing_extra(package: str, extra: str) -> NoReturn:
    """
    Print one line naming the extra to install, then exit with status 1.

    :param package: Name of the missing package, for example ``typer``.
    :param extra: Name of the extra that provides it, for example ``cli``.
    :raises SystemExit: Always, with status 1 and no traceback.
    """
    hint = f'pip install "collective.html2blocks[{extra}]"'
    sys.stderr.write(f"{package} is not installed. Install it with: {hint}\n")
    raise SystemExit(1)

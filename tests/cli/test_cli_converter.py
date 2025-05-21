from collective.html2blocks.cli import app
from typer.testing import CliRunner

import pytest


runner = CliRunner()


@pytest.mark.parametrize(
    "src,dst,exit_code,msg",
    [
        ["valid.html", "valid.json", 0, "Converted"],
        ["invalid.html", "valid.json", 1, "invalid.html does not exist"],
    ],
)
def test_cli_converter(html_dir, src: str, dst: str, exit_code: int, msg: str):
    payload = [
        "convert",
        f"{html_dir}/{src}",
        f"{html_dir}/{dst}",
    ]
    result = runner.invoke(app, payload)
    assert result.exit_code == exit_code
    assert msg in result.stdout

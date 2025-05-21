from collective.html2blocks import __version__
from collective.html2blocks.cli import app
from typer.testing import CliRunner


runner = CliRunner()


def test_cli_info_version():
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert f"# collective.html2blocks - {__version__}" in result.stdout


def test_cli_info_converters(caplog):
    caplog.clear()
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    levels = {record.levelname for record in caplog.records}
    assert levels == {"INFO"}
    messages = [record.message for record in caplog.records]
    assert "## Block Converters" in messages
    assert "## Element Converters" in messages

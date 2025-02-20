from collective.html2blocks import __version__
from collective.html2blocks import cli


def test_tool_information(caplog):
    caplog.clear()
    cli.tool_information()
    levels = {record.levelname for record in caplog.records}
    assert levels == {"INFO"}
    messages = [record.message for record in caplog.records]
    assert messages[0] == f"# collective.html2blocks - {__version__}"
    assert "## Block Converters" in messages
    assert "## Element Converters" in messages

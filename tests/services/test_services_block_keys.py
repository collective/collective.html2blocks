from collective.html2blocks import converter

import pytest


SOURCES = [
    "<table><tr><td>x</td></tr></table>",
    '<iframe src="https://example.org/embed" height="300px"></iframe>',
    '<img src="https://example.org/i.png" alt="An image" title="A title">',
    '<video src="https://example.org/v.mp4"></video>',
]


def _strip(value):
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if k != "key"}
    if isinstance(value, list):
        return [_strip(item) for item in value]
    return value


@pytest.mark.parametrize("source", SOURCES)
def test_services_html_keeps_block_keys(client, source: str):
    """The response model must not drop the keys specific to each block type."""
    response = client.post("/html", json={"html": source})
    assert response.status_code == 200, response.text
    assert _strip(response.json()) == _strip(converter.html_to_blocks(source))


@pytest.mark.parametrize("source", SOURCES)
def test_services_volto_keeps_block_keys(client, source: str):
    response = client.post("/volto", json={"html": source})
    assert response.status_code == 200, response.text
    blocks = list(response.json()["blocks"].values())
    assert _strip(blocks) == _strip(converter.html_to_blocks(source))


def test_services_markdown_keeps_block_keys(client):
    source = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    response = client.post("/markdown", json={"markdown": source})
    assert response.status_code == 200, response.text
    assert _strip(response.json()) == _strip(converter.markdown_to_blocks(source))

from collective.html2blocks import converter

import pytest


MARKDOWN = "# Title\n\nHello **world**.\n"
HTML = "<h1>Title</h1>\n<p>Hello <strong>world</strong>.</p>"


def test_services_markdown(client, strip_keys):
    """The /markdown endpoint converts Markdown like /html converts HTML."""
    response = client.post("/markdown", json={"markdown": MARKDOWN})
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    assert data, "Markdown produced no blocks"
    expected = converter.html_to_blocks(HTML)
    assert strip_keys(data) == strip_keys(expected)


def test_services_markdown_matches_html_endpoint(client, strip_keys):
    markdown_response = client.post("/markdown", json={"markdown": MARKDOWN})
    html_response = client.post("/html", json={"html": HTML})
    assert strip_keys(markdown_response.json()) == strip_keys(html_response.json())


def test_services_markdown_fail_converter(client):
    """The /markdown endpoint rejects unsupported converters like /html does."""
    response = client.post(
        "/markdown", json={"markdown": MARKDOWN, "converter": "draftjs"}
    )
    assert response.status_code == 400, f"Failed: {response.text}"
    assert response.json()["detail"] == "Unsupported converter: draftjs"


def test_services_volto_markdown_format(client, strip_keys):
    """The /volto endpoint reads ``html`` as Markdown when ``format`` says so."""
    response = client.post("/volto", json={"html": MARKDOWN, "format": "markdown"})
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    expected = converter.volto_blocks(MARKDOWN, source_format="markdown")
    items = data["blocks_layout"]["items"]
    assert items, "Markdown produced no layout items"
    assert [strip_keys(data["blocks"][i]) for i in items] == [
        strip_keys(expected["blocks"][i]) for i in expected["blocks_layout"]["items"]
    ]


def test_services_volto_default_format_is_html(client, strip_keys):
    response = client.post("/volto", json={"html": HTML})
    assert response.status_code == 200, f"Failed: {response.text}"
    expected = converter.volto_blocks(HTML)
    data = response.json()
    assert [strip_keys(data["blocks"][i]) for i in data["blocks_layout"]["items"]] == [
        strip_keys(expected["blocks"][i]) for i in expected["blocks_layout"]["items"]
    ]


@pytest.mark.parametrize("value", ["rst", "MARKDOWN", ""])
def test_services_volto_invalid_format(client, value):
    response = client.post("/volto", json={"html": HTML, "format": value})
    assert response.status_code == 422, f"Failed: {response.text}"

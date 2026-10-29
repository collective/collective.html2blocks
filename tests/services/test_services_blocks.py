from collective.html2blocks import registry

import pytest


HTML = "<p>a</p><pre>ls\n</pre><table><tr><td>x</td></tr></table>"
MARKDOWN = "a\n\n```sh\nls\n```\n\n| a | b |\n|---|---|\n| 1 | 2 |\n"


def test_services_blocks(client):
    response = client.get("/blocks")
    assert response.status_code == 200
    assert response.json() == registry.report_blocks()


def _types_volto(data: dict) -> list[str]:
    return [data["blocks"][item]["@type"] for item in data["blocks_layout"]["items"]]


@pytest.mark.parametrize(
    "path,payload,extract",
    [
        ["/html", {"html": HTML}, lambda data: [b["@type"] for b in data]],
        ["/markdown", {"markdown": MARKDOWN}, lambda data: [b["@type"] for b in data]],
        ["/volto", {"html": HTML}, _types_volto],
        ["/volto", {"html": MARKDOWN, "format": "markdown"}, _types_volto],
    ],
)
@pytest.mark.parametrize(
    "blocks,expected",
    [
        [None, ["slate", "slate", "slateTable"]],
        [{"codeBlock": True}, ["slate", "codeBlock", "slateTable"]],
        [{"codeBlock": {"style": "light"}}, ["slate", "codeBlock", "slateTable"]],
        [{"slateTable": False}, ["slate", "slate", "slate"]],
    ],
)
def test_services_blocks_field(
    client, path: str, payload: dict, extract, blocks, expected: list
):
    if blocks is not None:
        payload = {**payload, "blocks": blocks}
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    assert extract(response.json()) == expected


def test_services_blocks_field_options(client):
    payload = {"html": "<pre>ls</pre>", "blocks": {"codeBlock": {"style": "light"}}}
    response = client.post("/html", json=payload)
    assert response.status_code == 200, response.text
    assert response.json()[0]["style"] == "light"


@pytest.mark.parametrize("path", ["/html", "/markdown", "/volto"])
@pytest.mark.parametrize(
    "blocks,detail",
    [
        [{"accordion": True}, "Unknown block type accordion"],
        [{"slate": False}, "Block type slate cannot be disabled"],
        [{"codeBlock": {"theme": "x"}}, "Unknown option theme"],
        [{"codeBlock": {"showLineNumbers": "yes"}}, "must be bool, not str"],
    ],
)
def test_services_blocks_field_invalid(client, path: str, blocks: dict, detail: str):
    key = "markdown" if path == "/markdown" else "html"
    response = client.post(path, json={key: "<p>x</p>", "blocks": blocks})
    assert response.status_code == 400
    assert detail in response.json()["detail"]

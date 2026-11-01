from collective.html2blocks import converter

import pytest


HTML = "<h1>Hi</h1><p>Hello <strong>world</strong></p>"


def test_services_volto_plate(
    traverse, client, name, src, default_blocks, title, path, expected
):
    """Test the /volto endpoint with the plate converter."""
    payload = {
        "html": src,
        "converter": "plate",
        "title": title,
        "default_blocks": default_blocks,
    }
    response = client.post("/volto", json=payload)
    assert response.status_code == 200, f"Failed for {name}: {response.text}"
    value = traverse(response.json(), path)
    assert value == expected, (
        f"Failed for {name}: {path}: expected {expected}, got {value}"
    )


def test_services_slate2plate(traverse, client, name, content, path, expected):
    """Test the /slate2plate endpoint."""
    response = client.post("/slate2plate", json=content)
    assert response.status_code == 200, f"Failed for {name}: {response.text}"
    value = traverse(response.json(), path)
    assert value == expected, (
        f"Failed for {name}: {path}: expected {expected}, got {value}"
    )


@pytest.mark.parametrize(
    "path,payload",
    [["/html", {"html": HTML}], ["/volto", {"html": HTML}]],
)
def test_services_slate_is_the_default(client, path: str, payload: dict):
    response = client.post(path, json=payload)
    assert response.status_code == 200, response.text
    assert "__somersault__" not in response.text


def test_services_markdown_plate(client):
    payload = {"markdown": "# Hi", "converter": "plate"}
    response = client.post("/markdown", json=payload)
    assert response.status_code == 200, response.text
    assert response.json() == converter.markdown_to_blocks("# Hi", converter="plate")


@pytest.mark.parametrize(
    "path,payload",
    [
        ["/html", {"html": HTML}],
        ["/markdown", {"markdown": HTML}],
        ["/volto", {"html": HTML}],
    ],
)
def test_services_unknown_converter(client, path: str, payload: dict):
    response = client.post(path, json={**payload, "converter": "draftjs"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported converter: draftjs"


def test_services_slate2plate_needs_blocks(client):
    assert client.post("/slate2plate", json={"title": "x"}).status_code == 422

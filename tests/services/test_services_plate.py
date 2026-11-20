from collective.html2blocks import converter

import pytest


HTML = "<h1>Hi</h1><p>Hello <strong>world</strong></p>"


CONTENT = {
    "title": "Welcome",
    "blocks": {"a": {"@type": "title"}},
    "blocks_layout": {"items": ["a"]},
}

# Key in ``blocks`` and ``@type`` of the block of the Plate value, per format.
BODY = {"main": ("main", "plate"), "somersault": ("__somersault__", "__somersault__")}


def test_services_volto_plate(
    traverse, client, name, src, default_blocks, title, plate_format, path, expected
):
    """Test the /volto endpoint with the plate converter."""
    payload = {
        "html": src,
        "converter": "plate",
        "title": title,
        "default_blocks": default_blocks,
    }
    if plate_format is not None:
        payload["plate_format"] = plate_format
    response = client.post("/volto", json=payload)
    assert response.status_code == 200, f"Failed for {name}: {response.text}"
    value = traverse(response.json(), path)
    assert value == expected, (
        f"Failed for {name}: {path}: expected {expected}, got {value}"
    )


def test_services_slate2plate(
    traverse, client, name, content, plate_format, path, expected
):
    """Test the /slate2plate endpoint."""
    params = {} if plate_format is None else {"plate_format": plate_format}
    response = client.post("/slate2plate", json=content, params=params)
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
    assert '"plate"' not in response.text


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_services_markdown_plate(client, plate_format: str):
    payload = {"markdown": "# Hi", "converter": "plate", "plate_format": plate_format}
    response = client.post("/markdown", json=payload)
    assert response.status_code == 200, response.text
    expected = converter.markdown_to_blocks(
        "# Hi", converter="plate", plate_format=plate_format
    )
    assert response.json() == expected
    assert response.json()[0]["@type"] == BODY[plate_format][1]


def test_services_markdown_plate_format_defaults_to_main(client):
    response = client.post("/markdown", json={"markdown": "# Hi", "converter": "plate"})
    assert response.status_code == 200, response.text
    assert response.json() == converter.markdown_to_blocks("# Hi", converter="plate")
    assert response.json()[0]["@type"] == "plate"


@pytest.mark.parametrize(
    "path,payload",
    [
        ["/html", {"html": HTML}],
        ["/markdown", {"markdown": HTML}],
        ["/volto", {"html": HTML}],
    ],
)
@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_services_plate_format_field_matches_python(
    client, path: str, payload: dict, plate_format: str
):
    """Each endpoint returns what the Python function returns for the same format."""
    body = {**payload, "converter": "plate", "plate_format": plate_format}
    response = client.post(path, json=body)
    assert response.status_code == 200, response.text
    source = payload.get("html", payload.get("markdown"))
    func = {
        "/html": converter.html_to_blocks,
        "/markdown": converter.markdown_to_blocks,
        "/volto": converter.volto_blocks,
    }[path]
    assert response.json() == func(source, converter="plate", plate_format=plate_format)


@pytest.mark.parametrize("plate_format", ["main", "somersault"])
def test_services_slate2plate_matches_python(client, plate_format: str):
    response = client.post(
        "/slate2plate", json=CONTENT, params={"plate_format": plate_format}
    )
    assert response.status_code == 200, response.text
    assert response.json() == converter.slate_to_plate(
        CONTENT, plate_format=plate_format
    )
    key, block_type = BODY[plate_format]
    assert response.json()["blocks"][key]["@type"] == block_type


def test_services_slate2plate_format_is_not_a_content_key(client):
    """``plate_format`` is a query parameter, so it never lands in the content."""
    response = client.post(
        "/slate2plate", json=CONTENT, params={"plate_format": "somersault"}
    )
    assert response.status_code == 200, response.text
    assert "plate_format" not in response.json()


def test_services_slate2plate_ignores_a_body_plate_format(client):
    """The body is the content item: a ``plate_format`` key in it is content."""
    body = {**CONTENT, "plate_format": "somersault"}
    response = client.post("/slate2plate", json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["plate_format"] == "somersault"
    assert set(data["blocks"]) == {"a", "main"}


@pytest.mark.parametrize(
    "path,payload",
    [
        ["/html", {"html": HTML, "converter": "plate"}],
        ["/html", {"html": HTML}],
        ["/markdown", {"markdown": HTML, "converter": "plate"}],
        ["/volto", {"html": HTML, "converter": "plate"}],
        ["/volto", {"html": HTML}],
    ],
)
@pytest.mark.parametrize("plate_format", ["legacy", "", "plate", "__somersault__"])
def test_services_unknown_plate_format(
    client, path: str, payload: dict, plate_format: str
):
    response = client.post(path, json={**payload, "plate_format": plate_format})
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == f"Unsupported Plate format: {plate_format}"


@pytest.mark.parametrize("plate_format", ["legacy", "", "plate", "__somersault__"])
def test_services_slate2plate_unknown_plate_format(client, plate_format: str):
    response = client.post(
        "/slate2plate", json=CONTENT, params={"plate_format": plate_format}
    )
    assert response.status_code == 400, response.text
    assert response.json()["detail"] == f"Unsupported Plate format: {plate_format}"


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

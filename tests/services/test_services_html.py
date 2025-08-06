import pytest


def test_services_html(traverse, client, name, src, converter, path, expected):
    """Test the /html endpoint."""
    payload = {
        "html": src,
        "converter": converter,
    }
    response = client.post("/html", json=payload)
    assert response.status_code == 200, f"Failed for {name}: {response.text}"
    data = response.json()
    value = traverse(data, path)
    assert value == expected, (
        f"Failed for {name}: {path}: expected {expected}, got {value}"
    )


@pytest.mark.parametrize(
    "src,converter",
    [
        ("<p>Hello World</p>", "draftjs"),
        ("<p>Hello World</p>", "invalid"),
    ],
)
def test_services_html_fail_converter(client, src, converter):
    """The /html endpoint will fail if the converter is invalid."""
    payload = {
        "html": src,
        "converter": converter,
    }
    response = client.post("/html", json=payload)
    assert response.status_code == 400, f"Failed: {response.text}"
    data = response.json()
    assert data["detail"] == f"Unsupported converter: {converter}", (
        f"Unexpected error message: {data['detail']}"
    )

from collective.html2blocks import __version__

import pytest


@pytest.mark.parametrize(
    "key,expected",
    [
        ["title", "Blocks Conversion Tool"],
        ["version", __version__],
    ],
)
def test_services_root(client, key: str, expected: str):
    response = client.get("/")
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    assert data[key] == expected

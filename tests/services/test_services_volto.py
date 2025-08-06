def test_services_volto(
    traverse, client, name, src, default_blocks, additional_blocks, path, expected
):
    """Test the /volto endpoint."""
    payload = {
        "html": src,
        "default_blocks": default_blocks,
        "additional_blocks": additional_blocks,
    }
    response = client.post("/volto", json=payload)
    assert response.status_code == 200, f"Failed for {name}: {response.text}"
    data = response.json()
    value = traverse(data, path)
    assert value == expected, (
        f"Failed for {name}: {path}: expected {expected}, got {value}"
    )

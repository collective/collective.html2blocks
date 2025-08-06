def test_services_healthcheck(client):
    response = client.get("/ok")
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    assert data["status"] == "up"

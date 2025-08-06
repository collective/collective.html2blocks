from collective.html2blocks.services import app
from fastapi.testclient import TestClient

import pytest


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Fixture to create a FastAPI test client."""
    return TestClient(app)

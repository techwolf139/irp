import pytest
from fastapi.testclient import TestClient
from irp.main import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_app_title():
    assert app.title == "Divergent API"
    assert app.version == "4.0.0"

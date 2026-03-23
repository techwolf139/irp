import pytest


def test_config_loads():
    from irp.config import settings
    assert settings.database_url == "postgresql+asyncpg://localhost:5432/divergent"
    assert settings.sync_interval_seconds == 300


def test_health_endpoint():
    from fastapi.testclient import TestClient
    from irp.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

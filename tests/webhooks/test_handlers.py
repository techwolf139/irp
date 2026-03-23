import pytest
from fastapi.testclient import TestClient
from irp.main import app
from irp.webhooks.handlers import SupplierRiskChangedPayload


def test_webhook_supplier_risk_changed():
    client = TestClient(app)
    response = client.post(
        "/api/v1/webhook/supplier-risk-changed",
        json={
            "supplier_id": "SUP001",
            "old_score": 25.0,
            "new_score": 75.0,
            "risk_level_changed": True,
            "new_risk_level": "High"
        }
    )
    assert response.status_code == 200
    assert response.json() == {"status": "received"}

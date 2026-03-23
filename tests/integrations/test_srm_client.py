import pytest
from irp.integrations.srm_client import SRMSupplier, SRMPurchaseOrder


def test_srm_supplier_model():
    supplier = SRMSupplier(
        supplier_id="SUP001",
        name="Test Supplier",
        risk_score=25.0,
        risk_level="Low",
        is_discredited=False,
        rating=4.5,
        status="Active"
    )
    assert supplier.supplier_id == "SUP001"
    assert supplier.risk_level == "Low"
    assert supplier.rating == 4.5


def test_srm_purchase_order_model():
    po = SRMPurchaseOrder(
        po_id="PO001",
        supplier_id="SUP001",
        status="Active",
        items=[{"sku_id": "SKU001", "qty": 100}]
    )
    assert po.po_id == "PO001"
    assert len(po.items) == 1
    assert po.items[0]["qty"] == 100

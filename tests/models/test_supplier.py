import pytest
from irp.models.supplier import SupplierMaster, ProjectSupplierLink


def test_supplier_master_creation():
    supplier = SupplierMaster(
        supplier_id="SUP001",
        source_system="SRM",
        source_id="SRM001",
        name="Test Supplier",
        category="Manufacturer",
        risk_score=25.0,
        risk_level="Low",
        status="Active"
    )
    assert supplier.supplier_id == "SUP001"
    assert supplier.risk_level == "Low"
    assert supplier.status == "Active"


def test_supplier_master_full_fields():
    supplier = SupplierMaster(
        supplier_id="SUP002",
        source_system="SRM",
        source_id="SRM002",
        name="Full Supplier",
        category="Trader",
        scale="Large",
        business_reg_no="91110000000000001X",
        legal_person="John Doe",
        registered_capital=10000000.0,
        risk_score=15.0,
        risk_level="Low",
        is_discredited=False,
        litigation_count=0,
        admin_penalty_count=1,
        operation_status="Normal",
        rating=4.5,
        cooperation_count=10,
        status="Qualified"
    )
    assert supplier.business_reg_no == "91110000000000001X"
    assert supplier.legal_person == "John Doe"
    assert supplier.registered_capital == 10000000.0
    assert supplier.rating == 4.5
    assert supplier.cooperation_count == 10


def test_project_supplier_link():
    link = ProjectSupplierLink(
        project_id="PRJ001",
        supplier_id="SUP001",
        project_level_rating=4.5
    )
    assert link.project_id == "PRJ001"
    assert link.supplier_id == "SUP001"
    assert link.project_level_rating == 4.5


def test_project_supplier_link_with_tags():
    link = ProjectSupplierLink(
        project_id="PRJ002",
        supplier_id="SUP002",
        project_level_rating=4.0,
        project_level_tags=["IT", "Outsource", "Preferred"]
    )
    assert link.project_level_tags == ["IT", "Outsource", "Preferred"]

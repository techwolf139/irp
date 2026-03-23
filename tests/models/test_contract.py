import pytest
from datetime import date
from irp.models.contract import ContractMaster, PaymentPlan


def test_contract_master_creation():
    contract = ContractMaster(
        contract_id="CON001",
        source_system="SRM",
        source_id="SRM-CON001",
        title="框架采购协议",
        type="框架协议",
        total_amount=1000000.0,
        status="生效"
    )
    assert contract.contract_id == "CON001"
    assert contract.type == "框架协议"
    assert contract.total_amount == 1000000.0


def test_contract_master_full_fields():
    contract = ContractMaster(
        contract_id="CON002",
        source_system="PMS",
        source_id="PMS-CON002",
        contract_no="PM2024001",
        title="项目执行合同",
        type="执行合同",
        status="履行中",
        supplier_id="SUP001",
        project_id="PRJ001",
        total_amount=500000.0,
        currency="CNY",
        tax_rate=0.13,
        signed_date=date(2024, 1, 15),
        start_date=date(2024, 2, 1),
        end_date=date(2024, 12, 31),
        payment_terms="预付30%，交付后付70%",
        delivery_terms="FOB Shanghai",
        penalty_clause="延迟交付每日千分之一",
        child_contract_ids=["CON002-01", "CON002-02"],
        parent_contract_id=None
    )
    assert contract.contract_no == "PM2024001"
    assert contract.supplier_id == "SUP001"
    assert contract.project_id == "PRJ001"
    assert contract.currency == "CNY"
    assert contract.tax_rate == 0.13


def test_contract_master_child_contracts():
    contract = ContractMaster(
        contract_id="CON003",
        source_system="SRM",
        source_id="SRM-CON003",
        title="框架协议",
        type="框架协议",
        child_contract_ids=["CON003-01", "CON003-02"]
    )
    assert len(contract.child_contract_ids) == 2


def test_payment_plan():
    plan = PaymentPlan(
        contract_id="CON001",
        milestone="首付款",
        amount=300000.0,
        due_date=date(2024, 6, 1),
        status="待付款"
    )
    assert plan.milestone == "首付款"
    assert plan.amount == 300000.0
    assert plan.status == "待付款"


def test_payment_plan_with_invoices():
    plan = PaymentPlan(
        contract_id="CON001",
        milestone="尾款",
        amount=700000.0,
        due_date=date(2024, 12, 31),
        status="已付款",
        paid_amount=700000.0,
        invoice_ids=["INV001", "INV002"]
    )
    assert plan.invoice_ids == ["INV001", "INV002"]
    assert plan.paid_amount == 700000.0

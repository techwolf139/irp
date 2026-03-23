import pytest
from datetime import date
from irp.models.fund import FundFlow, BudgetView


def test_fund_flow_creation():
    flow = FundFlow(
        record_id="FF001",
        date=date(2024, 3, 1),
        type="支出",
        amount=10000.0,
        source_system="SRM",
        category="采购支出",
        supplier_id="SUP001"
    )
    assert flow.amount == 10000.0
    assert flow.type == "支出"


def test_fund_flow_full_fields():
    flow = FundFlow(
        record_id="FF002",
        date=date(2024, 3, 15),
        type="收入",
        amount=50000.0,
        currency="CNY",
        source_system="OMS",
        source_id="OMS001",
        category="销售收入",
        sub_category="产品销售",
        project_id="PRJ001",
        supplier_id="SUP002",
        contract_id="CON001",
        description="项目收入"
    )
    assert flow.currency == "CNY"
    assert flow.project_id == "PRJ001"
    assert flow.contract_id == "CON001"


def test_budget_view_available():
    budget = BudgetView(
        project_id="PRJ001",
        budget_total=1000000.0,
        budget_spent=300000.0,
        budget_committed=200000.0
    )
    assert budget.budget_available == 500000.0


def test_budget_view_full_fields():
    budget = BudgetView(
        project_id="PRJ002",
        budget_total=2000000.0,
        budget_spent=500000.0,
        budget_committed=300000.0,
        categories={"人员成本": 300000, "设备成本": 200000}
    )
    assert budget.budget_total == 2000000.0
    assert budget.budget_available == 1200000.0
    assert budget.categories["人员成本"] == 300000


def test_budget_view_zero_budget():
    budget = BudgetView(
        project_id="PRJ003",
        budget_total=0.0,
        budget_spent=0.0,
        budget_committed=0.0
    )
    assert budget.budget_available == 0.0

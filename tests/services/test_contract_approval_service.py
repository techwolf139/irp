import pytest
from irp.services.contract_approval_service import (
    ContractApprovalFlow,
    ContractType,
    ApprovalStep
)


def test_contract_approval_flow_purchase():
    flow = ContractApprovalFlow.get_flow(ContractType.PURCHASE)
    assert len(flow) == 4
    assert flow[0].step_name == "创建"
    assert flow[1].step_name == "采购负责人审批"


def test_contract_approval_flow_outsource():
    flow = ContractApprovalFlow.get_flow(ContractType.OUTSOURCE)
    assert len(flow) == 3
    assert flow[1].step_name == "项目负责人审批"


def test_contract_approval_flow_framework():
    flow = ContractApprovalFlow.get_flow(ContractType.FRAMEWORK)
    assert len(flow) == 2
    assert flow[0].step_name == "创建"
    assert flow[1].step_name == "法务审批"


def test_create_approval_record():
    record = ContractApprovalFlow.create_approval_record("CON001", ContractType.PURCHASE)
    assert record["contract_id"] == "CON001"
    assert record["current_step"] == 0
    assert len(record["steps"]) == 4
    assert record["status"] == "pending"


def test_create_approval_record_outsource():
    record = ContractApprovalFlow.create_approval_record("CON002", ContractType.OUTSOURCE)
    assert record["contract_id"] == "CON002"
    assert len(record["steps"]) == 3
    assert record["steps"][1]["step_name"] == "项目负责人审批"


def test_approval_step_defaults():
    step = ApprovalStep(step_name="创建", approver_role="采购员")
    assert step.status == "pending"
    assert step.approver_id is None
    assert step.comment is None
    assert step.approved_at is None

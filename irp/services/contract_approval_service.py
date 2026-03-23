from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ContractType(str, Enum):
    PURCHASE = "采购合同"
    OUTSOURCE = "外包合同"
    FRAMEWORK = "框架协议"


class ApprovalStep(BaseModel):
    step_name: str
    approver_role: str
    status: str = "pending"
    approver_id: Optional[str] = None
    comment: Optional[str] = None
    approved_at: Optional[datetime] = None


class ContractApprovalFlow:
    FLOW_MAP = {
        ContractType.PURCHASE: [
            ApprovalStep(step_name="创建", approver_role="采购员"),
            ApprovalStep(step_name="采购负责人审批", approver_role="采购负责人"),
            ApprovalStep(step_name="法务审批", approver_role="法务"),
            ApprovalStep(step_name="财务审批", approver_role="财务"),
        ],
        ContractType.OUTSOURCE: [
            ApprovalStep(step_name="创建", approver_role="采购员"),
            ApprovalStep(step_name="项目负责人审批", approver_role="项目负责人"),
            ApprovalStep(step_name="法务审批", approver_role="法务"),
        ],
        ContractType.FRAMEWORK: [
            ApprovalStep(step_name="创建", approver_role="采购员"),
            ApprovalStep(step_name="法务审批", approver_role="法务"),
        ],
    }

    @classmethod
    def get_flow(cls, contract_type: ContractType) -> List[ApprovalStep]:
        return cls.FLOW_MAP.get(contract_type, cls.FLOW_MAP[ContractType.FRAMEWORK])

    @classmethod
    def create_approval_record(cls, contract_id: str, contract_type: ContractType) -> dict:
        flow = cls.get_flow(contract_type)
        return {
            "contract_id": contract_id,
            "current_step": 0,
            "steps": [step.model_dump() for step in flow],
            "status": "pending"
        }

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from irp.core.database import get_db
from irp.models.contract import ContractMaster, PaymentPlan
from irp.services.contract_approval_service import ContractApprovalFlow, ContractType


class ContractResponse(BaseModel):
    contract_id: str
    title: str
    type: Optional[str]
    status: str
    supplier_id: Optional[str]
    project_id: Optional[str]
    total_amount: float
    currency: str
    signed_date: Optional[date]
    start_date: Optional[date]
    end_date: Optional[date]

    class Config:
        from_attributes = True


class ContractDetailResponse(ContractResponse):
    contract_no: Optional[str]
    source_system: str
    source_id: str
    tax_rate: float
    payment_terms: Optional[str]
    delivery_terms: Optional[str]
    penalty_clause: Optional[str]
    child_contract_ids: List[str]
    parent_contract_id: Optional[str]


class ContractStatsResponse(BaseModel):
    total: int
    draft: int
    active: int
    completed: int
    terminated: int


class ApprovalRecordResponse(BaseModel):
    contract_id: str
    current_step: int
    steps: List[dict]
    status: str


router = APIRouter()


@router.get("/contracts", response_model=List[ContractResponse])
async def list_contracts(
    status: Optional[str] = None,
    supplier_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ContractMaster)
    if status:
        query = query.where(ContractMaster.status == status)
    if supplier_id:
        query = query.where(ContractMaster.supplier_id == supplier_id)

    result = await db.execute(query)
    contracts = result.scalars().all()
    return [
        ContractResponse(
            contract_id=c.contract_id,
            title=c.title,
            type=c.type,
            status=c.status,
            supplier_id=c.supplier_id,
            project_id=c.project_id,
            total_amount=c.total_amount or 0,
            currency=c.currency or "CNY",
            signed_date=c.signed_date,
            start_date=c.start_date,
            end_date=c.end_date
        )
        for c in contracts
    ]


@router.get("/contracts/{contract_id}", response_model=ContractDetailResponse)
async def get_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ContractMaster).where(ContractMaster.contract_id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return ContractDetailResponse(
        contract_id=contract.contract_id,
        title=contract.title,
        type=contract.type,
        status=contract.status,
        supplier_id=contract.supplier_id,
        project_id=contract.project_id,
        total_amount=contract.total_amount or 0,
        currency=contract.currency or "CNY",
        signed_date=contract.signed_date,
        start_date=contract.start_date,
        end_date=contract.end_date,
        contract_no=contract.contract_no,
        source_system=contract.source_system,
        source_id=contract.source_id,
        tax_rate=contract.tax_rate or 0.13,
        payment_terms=contract.payment_terms,
        delivery_terms=contract.delivery_terms,
        penalty_clause=contract.penalty_clause,
        child_contract_ids=contract.child_contract_ids or [],
        parent_contract_id=contract.parent_contract_id
    )


@router.get("/contracts/stats", response_model=ContractStatsResponse)
async def get_contract_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(ContractMaster.id)))
    total = total_result.scalar() or 0

    draft_result = await db.execute(
        select(func.count(ContractMaster.id)).where(ContractMaster.status == "草稿")
    )
    draft = draft_result.scalar() or 0

    active_result = await db.execute(
        select(func.count(ContractMaster.id)).where(ContractMaster.status == "履行中")
    )
    active = active_result.scalar() or 0

    completed_result = await db.execute(
        select(func.count(ContractMaster.id)).where(ContractMaster.status == "已完成")
    )
    completed = completed_result.scalar() or 0

    terminated_result = await db.execute(
        select(func.count(ContractMaster.id)).where(ContractMaster.status == "终止")
    )
    terminated = terminated_result.scalar() or 0

    return ContractStatsResponse(
        total=total,
        draft=draft,
        active=active,
        completed=completed,
        terminated=terminated
    )


@router.post("/contracts/{contract_id}/approval", response_model=ApprovalRecordResponse)
async def create_approval_flow(
    contract_id: str,
    contract_type: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ContractMaster).where(ContractMaster.contract_id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    try:
        ctype = ContractType(contract_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid contract type: {contract_type}")

    record = ContractApprovalFlow.create_approval_record(contract_id, ctype)
    return ApprovalRecordResponse(**record)

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from irp.core.database import get_db
from irp.models.contract import ContractMaster, PaymentPlan
from irp.services.contract_approval_service import ContractApprovalFlow, ContractType


def _extract_value(value):
    """从任何类型（包括 SQLAlchemy Column）提取实际值"""
    if isinstance(value, Column):
        return None
    return value


class ContractResponse(BaseModel):
    contract_id: str
    title: str
    type: Optional[str] = None
    status: str
    supplier_id: Optional[str] = None
    project_id: Optional[str] = None
    total_amount: float = 0.0
    currency: str = "CNY"
    signed_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> 'ContractResponse':
        """从 SQLAlchemy 模型创建响应"""
        return cls(
            contract_id=model.contract_id or "",
            title=model.title or "",
            type=model.type,
            status=model.status,
            supplier_id=model.supplier_id,
            project_id=model.project_id,
            total_amount=float(model.total_amount or 0),
            currency=model.currency or "CNY",
            signed_date=model.signed_date,
            start_date=model.start_date,
            end_date=model.end_date
        )


class ContractDetailResponse(ContractResponse):
    contract_no: Optional[str] = None
    source_system: str = ""
    source_id: str = ""
    tax_rate: float = 0.0
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    penalty_clause: Optional[str] = None
    child_contract_ids: List[str] = []
    parent_contract_id: Optional[str] = None

    @classmethod
    def from_model(cls, model) -> 'ContractDetailResponse':
        """从 SQLAlchemy 模型创建详细响应"""
        return cls(
            contract_id=model.contract_id or "",
            title=model.title or "",
            type=model.type,
            status=model.status,
            supplier_id=model.supplier_id,
            project_id=model.project_id,
            total_amount=float(model.total_amount or 0),
            currency=model.currency or "CNY",
            signed_date=model.signed_date,
            start_date=model.start_date,
            end_date=model.end_date,
            contract_no=model.contract_no,
            source_system=model.source_system or "",
            source_id=model.source_id or "",
            tax_rate=float(model.tax_rate or 0.13),
            payment_terms=model.payment_terms,
            delivery_terms=model.delivery_terms,
            penalty_clause=model.penalty_clause,
            child_contract_ids=list(model.child_contract_ids or []),
            parent_contract_id=model.parent_contract_id
        )


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
    return [ContractResponse.from_model(c) for c in contracts]


    @router.get("/contracts/{contract_id}", response_model=ContractDetailResponse)
    async def get_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(
            select(ContractMaster).where(ContractMaster.contract_id == contract_id)
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return ContractDetailResponse.from_model(contract)


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


class ContractCreateRequest(BaseModel):
    contract_id: str
    title: str
    type: Optional[str] = None
    supplier_id: Optional[str] = None
    project_id: Optional[str] = None
    total_amount: float = 0
    currency: str = "CNY"
    signed_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    contract_no: Optional[str] = None
    tax_rate: float = 0.13
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    penalty_clause: Optional[str] = None


class ContractUpdateRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None
    signed_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    penalty_clause: Optional[str] = None


@router.post("/contracts", response_model=ContractResponse)
async def create_contract(
    request: ContractCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(
        select(ContractMaster).where(ContractMaster.contract_id == request.contract_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Contract ID already exists")

    contract = ContractMaster(
        contract_id=request.contract_id,
        source_system="IRP",
        source_id=request.contract_id,
        contract_no=request.contract_no,
        title=request.title,
        type=request.type,
        status="草稿",
        supplier_id=request.supplier_id,
        project_id=request.project_id,
        total_amount=request.total_amount,
        currency=request.currency,
        tax_rate=request.tax_rate,
        signed_date=request.signed_date,
        start_date=request.start_date,
        end_date=request.end_date,
        payment_terms=request.payment_terms,
        delivery_terms=request.delivery_terms,
        penalty_clause=request.penalty_clause
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)

    return ContractResponse.from_model(contract)


@router.put("/contracts/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: str,
    request: ContractUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ContractMaster).where(ContractMaster.contract_id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contract, field, value)
    contract.updated_at = datetime.utcnow()  # type: ignore
    await db.commit()
    await db.refresh(contract)

    return ContractResponse.from_model(contract)


@router.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ContractMaster).where(ContractMaster.contract_id == contract_id)
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    await db.delete(contract)
    await db.commit()

    return {"message": "Contract deleted successfully"}

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from irp.core.database import get_db
from irp.models.supplier import SupplierMaster, ProjectSupplierLink


class SupplierResponse(BaseModel):
    supplier_id: str
    name: str
    risk_level: Optional[str] = None
    risk_score: float = 0.0
    rating: float = 0.0
    status: str = "Pending"

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_model(cls, model) -> 'SupplierResponse':
        """从 SQLAlchemy 模型创建响应"""
        return cls(
            supplier_id=model.supplier_id or "",
            name=model.name or "",
            risk_level=model.risk_level,
            risk_score=float(model.risk_score or 0),
            rating=float(model.rating or 0),
            status=model.status or "Pending"
        )


class SupplierStatsResponse(BaseModel):
    total: int
    low_risk: int
    medium_risk: int


router = APIRouter()


@router.get("/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    risk_level: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(SupplierMaster)
    if risk_level:
        query = query.where(SupplierMaster.risk_level == risk_level)
    if status:
        query = query.where(SupplierMaster.status == status)

    result = await db.execute(query)
    suppliers = result.scalars().all()
    return [SupplierResponse.from_model(s) for s in suppliers]


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SupplierMaster).where(SupplierMaster.supplier_id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return SupplierResponse.from_model(supplier)


@router.get("/suppliers/stats", response_model=SupplierStatsResponse)
async def get_supplier_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count(SupplierMaster.id)))
    total = total_result.scalar() or 0

    low_risk_result = await db.execute(
        select(func.count(SupplierMaster.id))
        .where(SupplierMaster.risk_level == "Low")
    )
    low_risk = low_risk_result.scalar() or 0

    return SupplierStatsResponse(
        total=total,
        low_risk=low_risk,
        medium_risk=total - low_risk
    )


class SupplierCreateRequest(BaseModel):
    supplier_id: str
    name: str
    category: Optional[str] = None
    scale: Optional[str] = None
    business_reg_no: Optional[str] = None
    legal_person: Optional[str] = None
    registered_capital: Optional[float] = None
    risk_score: float = 0
    risk_level: Optional[str] = "Medium"
    is_discredited: bool = False
    rating: float = 0
    status: str = "待审核"


class SupplierUpdateRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    scale: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    rating: Optional[float] = None
    status: Optional[str] = None


@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(
    request: SupplierCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(
        select(SupplierMaster).where(SupplierMaster.supplier_id == request.supplier_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Supplier ID already exists")

    supplier = SupplierMaster(
        supplier_id=request.supplier_id,
        source_system="IRP",
        source_id=request.supplier_id,
        name=request.name,
        category=request.category,
        scale=request.scale,
        business_reg_no=request.business_reg_no,
        legal_person=request.legal_person,
        registered_capital=request.registered_capital,
        risk_score=request.risk_score,
        risk_level=request.risk_level,
        is_discredited=request.is_discredited,
        rating=request.rating,
        status=request.status
    )
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)

    return SupplierResponse.from_model(supplier)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    request: SupplierUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SupplierMaster).where(SupplierMaster.supplier_id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    supplier.updated_at = datetime.utcnow()  # type: ignore
    await db.commit()
    await db.refresh(supplier)

    return SupplierResponse.from_model(supplier)


@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SupplierMaster).where(SupplierMaster.supplier_id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    await db.delete(supplier)
    await db.commit()

    return {"message": "Supplier deleted successfully"}

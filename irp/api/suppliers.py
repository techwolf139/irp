from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from irp.core.database import get_db
from irp.models.supplier import SupplierMaster, ProjectSupplierLink


class SupplierResponse(BaseModel):
    supplier_id: str
    name: str
    risk_level: Optional[str]
    risk_score: float
    rating: float
    status: str

    class Config:
        from_attributes = True


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
    return [
        SupplierResponse(
            supplier_id=s.supplier_id,
            name=s.name,
            risk_level=s.risk_level,
            risk_score=s.risk_score or 0,
            rating=s.rating or 0,
            status=s.status
        )
        for s in suppliers
    ]


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SupplierMaster).where(SupplierMaster.supplier_id == supplier_id)
    )
    supplier = result.scalar_one_or_none()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return SupplierResponse(
        supplier_id=supplier.supplier_id,
        name=supplier.name,
        risk_level=supplier.risk_level,
        risk_score=supplier.risk_score or 0,
        rating=supplier.rating or 0,
        status=supplier.status
    )


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

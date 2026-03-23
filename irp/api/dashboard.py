from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from irp.core.database import get_db
from irp.models.supplier import SupplierMaster
from irp.models.inventory import InventoryView, ReplenishmentTask
from irp.models.resource import TaskRequest
from irp.models.fund import FundFlow


router = APIRouter()


@router.get("/dashboard/overview")
async def get_overview(db: AsyncSession = Depends(get_db)):
    supplier_result = await db.execute(select(func.count(SupplierMaster.id)))
    supplier_total = supplier_result.scalar() or 0

    low_risk_result = await db.execute(
        select(func.count(SupplierMaster.id)).where(SupplierMaster.risk_level == "Low")
    )
    supplier_low_risk = low_risk_result.scalar() or 0

    inventory_alerts_result = await db.execute(
        select(func.count(InventoryView.id)).where(InventoryView.stock_status == "预警")
    )
    inventory_alerts = inventory_alerts_result.scalar() or 0

    pending_tasks_result = await db.execute(
        select(func.count(TaskRequest.id)).where(TaskRequest.status == "pending")
    )
    pending_tasks = pending_tasks_result.scalar() or 0

    return {
        "suppliers": {
            "total": supplier_total,
            "low_risk": supplier_low_risk,
            "medium_risk": supplier_total - supplier_low_risk
        },
        "inventory": {
            "alert_count": inventory_alerts
        },
        "funds": {
            "monthly_expense": 0
        },
        "tasks": {
            "pending_count": pending_tasks
        }
    }


@router.get("/dashboard/resources")
async def get_resources_dashboard(db: AsyncSession = Depends(get_db)):
    return {
        "human": {
            "total": 0,
            "available": 0,
            "busy": 0
        },
        "ai": {
            "total": 0,
            "available": 0
        }
    }

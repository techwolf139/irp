import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.inventory import ReplenishmentTask, InventoryView
from irp.integrations.srm_client import SRMClient


class ReplenishmentService:
    def __init__(self, db: AsyncSession, srm_client: SRMClient, inventory_sync_service):
        self.db = db
        self.srm = srm_client
        self.inventory_sync = inventory_sync_service

    async def get_inventory(self, sku_id: str):
        result = await self.db.execute(
            select(InventoryView).where(InventoryView.sku_id == sku_id)
        )
        return result.scalar_one_or_none()

    async def check_and_create_replenishment(self, sku_id: str) -> tuple[bool, str]:
        needs_replenishment, reason = await self.inventory_sync.check_replenishment_needed(sku_id)

        if not needs_replenishment:
            return False, reason

        inventory = await self.get_inventory(sku_id)

        task = ReplenishmentTask(
            task_id=f"RPT-{uuid.uuid4().hex[:8]}",
            sku_id=sku_id,
            qty=inventory.reorder_qty,
            status="待采购",
            estimated_arrival=datetime.utcnow() + timedelta(days=inventory.lead_time_days)
        )

        self.db.add(task)
        await self.db.commit()

        return True, f"补货任务已创建: {task.task_id}"

    async def initiate_procurement(self, task_id: str) -> str:
        result = await self.db.execute(
            select(ReplenishmentTask).where(ReplenishmentTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"任务不存在: {task_id}")

        if task.status != "待采购":
            raise ValueError(f"任务状态错误: {task.status}")

        price_comparison = await self.srm.get_price_comparison(task.sku_id, task.qty)

        requisition_id = await self.srm.create_purchase_requisition([
            {
                "sku_id": task.sku_id,
                "qty": task.qty,
                "preferred_supplier_id": task.supplier_id
            }
        ])

        task.requisition_id = requisition_id
        task.status = "待人工确认"
        await self.db.commit()

        return requisition_id

    async def approve_and_order(self, task_id: str) -> str:
        result = await self.db.execute(
            select(ReplenishmentTask).where(ReplenishmentTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task or not task.requisition_id:
            raise ValueError("任务或采购申请不存在")

        po_id = await self.srm.confirm_purchase_order(task.requisition_id)

        task.status = "采购中"
        await self.db.commit()

        return po_id

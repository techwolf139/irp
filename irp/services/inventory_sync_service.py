from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.inventory import InventoryView, ReplenishmentTask
from irp.integrations.oms_client import OMSClient
from irp.integrations.srm_client import SRMClient


class InventorySyncService:
    def __init__(self, db: AsyncSession, oms_client: OMSClient, srm_client: SRMClient):
        self.db = db
        self.oms = oms_client
        self.srm = srm_client

    async def sync_from_oms(self):
        oms_inventory_list = await self.oms.list_inventory()

        for oms_inv in oms_inventory_list:
            result = await self.db.execute(
                select(InventoryView).where(InventoryView.sku_id == oms_inv.sku_id)
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.sellable_qty = oms_inv.sellable_qty
                existing.reserved_qty = oms_inv.reserved_qty
                existing.available_qty = oms_inv.available_qty
            else:
                inventory = InventoryView(
                    sku_id=oms_inv.sku_id,
                    sku_name=oms_inv.sku_name,
                    sellable_qty=oms_inv.sellable_qty,
                    reserved_qty=oms_inv.reserved_qty,
                    available_qty=oms_inv.available_qty
                )
                self.db.add(inventory)

        await self.db.commit()

    async def sync_in_transit_from_srm(self):
        purchase_orders = await self.srm.get_purchase_orders(status="采购中")

        for po in purchase_orders:
            for item in po.items:
                result = await self.db.execute(
                    select(InventoryView).where(InventoryView.sku_id == item["sku_id"])
                )
                inventory = result.scalar_one_or_none()
                if inventory:
                    inventory.in_transit_qty += item["qty"]

        await self.db.commit()

    async def check_replenishment_needed(self, sku_id: str) -> tuple[bool, str]:
        result = await self.db.execute(
            select(InventoryView).where(InventoryView.sku_id == sku_id)
        )
        inventory = result.scalar_one_or_none()

        if not inventory:
            return False, "SKU不存在"

        available_qty = inventory.available_qty  # type: ignore
        reorder_point = inventory.reorder_point  # type: ignore
        if available_qty < reorder_point:  # type: ignore
            return True, f"可用库存{available_qty} < 补货点{reorder_point}"

        return False, "库存充足"

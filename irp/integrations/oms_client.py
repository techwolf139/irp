import httpx
from typing import List, Optional
from pydantic import BaseModel


class OMSInventory(BaseModel):
    sku_id: str
    sku_name: str
    sellable_qty: int
    reserved_qty: int
    in_transit_qty: int = 0
    available_qty: int


class OMSClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_inventory(self, sku_id: str) -> Optional[OMSInventory]:
        response = await self.client.get(f"{self.base_url}/api/inventory/{sku_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        data["available_qty"] = data["sellable_qty"] - data["reserved_qty"]
        return OMSInventory(**data)

    async def list_inventory(self, stock_status: str = None) -> List[OMSInventory]:
        params = {}
        if stock_status:
            params["stock_status"] = stock_status
        response = await self.client.get(f"{self.base_url}/api/inventory", params=params)
        response.raise_for_status()
        items = response.json()
        for item in items:
            item["available_qty"] = item["sellable_qty"] - item["reserved_qty"]
        return [OMSInventory(**i) for i in items]

    async def close(self):
        await self.client.aclose()

import httpx
from typing import List, Optional
from pydantic import BaseModel
from irp.core.retry import retry_async, RetryConfig


class OMSInventory(BaseModel):
    sku_id: str
    sku_name: str
    sellable_qty: int
    reserved_qty: int
    in_transit_qty: int = 0
    available_qty: int


class OMSClient:
    def __init__(self, base_url: str, retry_config: Optional[RetryConfig] = None):
        self.base_url = base_url
        self.retry_config = retry_config or RetryConfig()
        self.client = httpx.AsyncClient(timeout=self.retry_config.timeout)

    @retry_async(max_retries=3, delay=1.0, backoff=2.0, exceptions=(httpx.HTTPError,))
    async def get_inventory(self, sku_id: str) -> Optional[OMSInventory]:
        response = await self.client.get(f"{self.base_url}/api/inventory/{sku_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        data["available_qty"] = data["sellable_qty"] - data["reserved_qty"]
        return OMSInventory(**data)

    @retry_async(max_retries=3, delay=1.0, backoff=2.0, exceptions=(httpx.HTTPError,))
    async def list_inventory(self, stock_status: Optional[str] = None) -> List[OMSInventory]:
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

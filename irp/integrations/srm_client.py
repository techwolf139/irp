import httpx
from typing import List, Optional
from pydantic import BaseModel


class SRMSupplier(BaseModel):
    supplier_id: str
    name: str
    business_reg_no: Optional[str] = None
    risk_score: float = 0
    risk_level: str = "Medium"
    is_discredited: bool = False
    rating: float = 0
    status: str = "Pending"


class SRMPurchaseOrder(BaseModel):
    po_id: str
    supplier_id: str
    status: str
    items: List[dict] = []


class SRMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_suppliers(self, risk_level: str = None) -> List[SRMSupplier]:
        params = {}
        if risk_level:
            params["risk_level"] = risk_level
        response = await self.client.get(f"{self.base_url}/api/suppliers", params=params)
        response.raise_for_status()
        return [SRMSupplier(**s) for s in response.json()]

    async def get_supplier(self, supplier_id: str) -> SRMSupplier:
        response = await self.client.get(f"{self.base_url}/api/suppliers/{supplier_id}")
        response.raise_for_status()
        return SRMSupplier(**response.json())

    async def create_purchase_requisition(self, items: List[dict]) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/purchase-requisitions",
            json={"items": items}
        )
        response.raise_for_status()
        return response.json()["requisition_id"]

    async def get_purchase_orders(self, supplier_id: str = None) -> List[SRMPurchaseOrder]:
        params = {}
        if supplier_id:
            params["supplier_id"] = supplier_id
        response = await self.client.get(f"{self.base_url}/api/purchase-orders", params=params)
        response.raise_for_status()
        return [SRMPurchaseOrder(**po) for po in response.json()]

    async def close(self):
        await self.client.aclose()

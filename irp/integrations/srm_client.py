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


class SRMContract(BaseModel):
    contract_id: str
    title: str
    type: str
    status: str
    supplier_id: Optional[str] = None
    total_amount: float = 0
    signed_date: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


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

    async def get_contracts(self) -> List[SRMContract]:
        response = await self.client.get(f"{self.base_url}/api/contracts")
        response.raise_for_status()
        return [SRMContract(**c) for c in response.json()]

    async def get_price_comparison(self, sku_id: str, qty: int) -> dict:
        response = await self.client.get(
            f"{self.base_url}/api/price-comparison",
            params={"sku_id": sku_id, "qty": qty}
        )
        response.raise_for_status()
        return response.json()

    async def confirm_purchase_order(self, requisition_id: str) -> str:
        response = await self.client.post(
            f"{self.base_url}/api/purchase-orders/confirm",
            json={"requisition_id": requisition_id}
        )
        response.raise_for_status()
        return response.json()["po_id"]

    async def close(self):
        await self.client.aclose()

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class SupplierRiskChangedPayload(BaseModel):
    supplier_id: str
    old_score: float
    new_score: float
    risk_level_changed: bool
    new_risk_level: Optional[str] = None


@router.post("/webhook/supplier-risk-changed")
async def handle_supplier_risk_changed(
    payload: SupplierRiskChangedPayload,
    request: Request
):
    service = getattr(request.app.state, "supplier_sync_service", None)

    print(f"Supplier {payload.supplier_id} risk changed: {payload.old_score} -> {payload.new_score}")

    if payload.risk_level_changed and payload.new_risk_level == "High":
        if service:
            await send_high_risk_alert(service, payload.supplier_id, payload.new_score)

    return {"status": "received"}


async def send_high_risk_alert(service, supplier_id: str, risk_score: float):
    pass

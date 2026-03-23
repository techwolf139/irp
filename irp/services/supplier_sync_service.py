from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.supplier import SupplierMaster
from irp.integrations.srm_client import SRMClient
from irp.integrations.pms_client import PMSClient


class SupplierSyncService:
    def __init__(self, db: AsyncSession, srm_client: SRMClient, pms_client: PMSClient):
        self.db = db
        self.srm = srm_client
        self.pms = pms_client

    async def sync_from_srm(self):
        srm_suppliers = await self.srm.get_suppliers()

        for srm_sup in srm_suppliers:
            result = await self.db.execute(
                select(SupplierMaster).where(
                    SupplierMaster.source_system == "SRM",
                    SupplierMaster.source_id == srm_sup.supplier_id
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.name = srm_sup.name
                existing.risk_score = srm_sup.risk_score
                existing.risk_level = srm_sup.risk_level
                existing.is_discredited = srm_sup.is_discredited
                existing.rating = srm_sup.rating
                existing.status = srm_sup.status
            else:
                supplier = SupplierMaster(
                    supplier_id=f"SRM-{srm_sup.supplier_id}",
                    source_system="SRM",
                    source_id=srm_sup.supplier_id,
                    name=srm_sup.name,
                    business_reg_no=srm_sup.business_reg_no,
                    risk_score=srm_sup.risk_score,
                    risk_level=srm_sup.risk_level,
                    is_discredited=srm_sup.is_discredited,
                    rating=srm_sup.rating,
                    status=srm_sup.status
                )
                self.db.add(supplier)

        await self.db.commit()

    async def get_supplier_stats(self) -> dict:
        total_result = await self.db.execute(select(SupplierMaster))
        all_suppliers = total_result.scalars().all()
        total_count = len(all_suppliers)

        low_risk_result = await self.db.execute(
            select(SupplierMaster).where(SupplierMaster.risk_level == "Low")
        )
        low_risk_count = len(low_risk_result.scalars().all())

        return {
            "total": total_count,
            "low_risk": low_risk_count,
            "medium_risk": total_count - low_risk_count
        }

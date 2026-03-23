from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.contract import ContractMaster, PaymentPlan
from irp.integrations.srm_client import SRMClient
from irp.integrations.pms_client import PMSClient


class ContractSyncService:
    def __init__(self, db: AsyncSession, srm_client: SRMClient, pms_client: PMSClient):
        self.db = db
        self.srm = srm_client
        self.pms = pms_client

    async def sync_from_srm(self):
        srm_contracts = await self.srm.get_contracts()

        for srm_con in srm_contracts:
            result = await self.db.execute(
                select(ContractMaster).where(
                    ContractMaster.source_system == "SRM",
                    ContractMaster.source_id == srm_con.contract_id
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.title = srm_con.title
                existing.status = srm_con.status
                existing.total_amount = srm_con.total_amount
            else:
                contract = ContractMaster(
                    contract_id=f"SRM-{srm_con.contract_id}",
                    source_system="SRM",
                    source_id=srm_con.contract_id,
                    title=srm_con.title,
                    type=srm_con.type,
                    status=srm_con.status,
                    supplier_id=srm_con.supplier_id,
                    total_amount=srm_con.total_amount
                )
                self.db.add(contract)

        await self.db.commit()

    async def link_pms_contract(self, srm_contract_id: str, pms_contract_id: str):
        result = await self.db.execute(
            select(ContractMaster).where(ContractMaster.contract_id == srm_contract_id)
        )
        parent = result.scalar_one_or_none()

        if parent:
            child = ContractMaster(
                contract_id=f"PMS-{pms_contract_id}",
                source_system="PMS",
                source_id=pms_contract_id,
                title=f"项目合同 - {pms_contract_id}",
                type="执行合同",
                parent_contract_id=srm_contract_id,
                supplier_id=parent.supplier_id
            )
            self.db.add(child)

            if parent.child_contract_ids is None:
                parent.child_contract_ids = []
            parent.child_contract_ids.append(child.contract_id)

            await self.db.commit()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.supplier import SupplierMaster, ProjectSupplierLink
from typing import List, Optional


class SupplierMappingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_link(
        self,
        project_id: str,
        supplier_id: str,
        rating: Optional[float] = None,
        tags: Optional[List[str]] = None
    ) -> ProjectSupplierLink:
        link = ProjectSupplierLink(
            project_id=project_id,
            supplier_id=supplier_id,
            project_level_rating=rating,
            project_level_tags=tags or []
        )
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def get_project_suppliers(self, project_id: str) -> List[dict]:
        result = await self.db.execute(
            select(ProjectSupplierLink, SupplierMaster)
            .join(SupplierMaster, ProjectSupplierLink.supplier_id == SupplierMaster.supplier_id)
            .where(ProjectSupplierLink.project_id == project_id)
        )
        links = []
        for link, supplier in result.all():
            links.append({
                "project_id": link.project_id,
                "supplier_id": link.supplier_id,
                "supplier_name": supplier.name,
                "project_level_rating": link.project_level_rating,
                "project_level_tags": link.project_level_tags,
                "supplier_risk_level": supplier.risk_level,
                "supplier_rating": supplier.rating
            })
        return links

    async def get_supplier_projects(self, supplier_id: str) -> List[dict]:
        result = await self.db.execute(
            select(ProjectSupplierLink)
            .where(ProjectSupplierLink.supplier_id == supplier_id)
        )
        return [
            {
                "project_id": link.project_id,
                "project_level_rating": link.project_level_rating,
                "project_level_tags": link.project_level_tags
            }
            for link in result.scalars().all()
        ]

    async def delete_link(self, project_id: str, supplier_id: str) -> bool:
        result = await self.db.execute(
            select(ProjectSupplierLink)
            .where(
                ProjectSupplierLink.project_id == project_id,
                ProjectSupplierLink.supplier_id == supplier_id
            )
        )
        link = result.scalar_one_or_none()
        if link:
            await self.db.delete(link)
            await self.db.commit()
            return True
        return False

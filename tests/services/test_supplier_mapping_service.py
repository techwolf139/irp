import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.supplier_mapping_service import SupplierMappingService


@pytest.mark.asyncio
async def test_create_link():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    service = SupplierMappingService(mock_db)
    link = await service.create_link(
        project_id="PRJ001",
        supplier_id="SUP001",
        rating=4.5,
        tags=["IT", "Preferred"]
    )

    assert link.project_id == "PRJ001"
    assert link.supplier_id == "SUP001"
    assert link.project_level_rating == 4.5
    assert link.project_level_tags == ["IT", "Preferred"]
    mock_db.add.assert_called_once()

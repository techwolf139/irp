import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.supplier_sync_service import SupplierSyncService


@pytest.mark.asyncio
async def test_get_supplier_stats():
    mock_db = AsyncMock()
    mock_srm = AsyncMock()
    mock_pms = AsyncMock()

    mock_all_result = MagicMock()
    mock_all_result.scalars.return_value.all.return_value = [
        MagicMock(supplier_id="SUP001"),
        MagicMock(supplier_id="SUP002"),
        MagicMock(supplier_id="SUP003"),
    ]
    mock_low_risk_result = MagicMock()
    mock_low_risk_result.scalars.return_value.all.return_value = [
        MagicMock(supplier_id="SUP001"),
    ]

    mock_db.execute.side_effect = [mock_all_result, mock_low_risk_result]

    service = SupplierSyncService(mock_db, mock_srm, mock_pms)
    stats = await service.get_supplier_stats()

    assert stats["total"] == 3
    assert stats["low_risk"] == 1
    assert stats["medium_risk"] == 2

import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.inventory_sync_service import InventorySyncService


@pytest.mark.asyncio
async def test_sync_from_oms():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()

    mock_oms = AsyncMock()
    mock_oms.list_inventory = AsyncMock(return_value=[
        MagicMock(
            sku_id="SKU001",
            sku_name="产品A",
            sellable_qty=100,
            reserved_qty=20,
            available_qty=80
        )
    ])

    mock_srm = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    service = InventorySyncService(mock_db, mock_oms, mock_srm)
    await service.sync_from_oms()

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_check_replenishment_needed():
    mock_db = MagicMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()

    service = InventorySyncService(mock_db, mock_oms, mock_srm)

    mock_inventory = MagicMock()
    mock_inventory.available_qty = 50
    mock_inventory.reorder_point = 100

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_inventory)
    mock_db.execute = AsyncMock(return_value=mock_result)

    needs_replenishment, reason = await service.check_replenishment_needed("SKU001")

    assert needs_replenishment is True
    assert "可用库存50 < 补货点100" in reason


@pytest.mark.asyncio
async def test_check_replenishment_needed_sufficient():
    mock_db = MagicMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()

    service = InventorySyncService(mock_db, mock_oms, mock_srm)

    mock_inventory = MagicMock()
    mock_inventory.available_qty = 150
    mock_inventory.reorder_point = 100

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_inventory)
    mock_db.execute = AsyncMock(return_value=mock_result)

    needs_replenishment, reason = await service.check_replenishment_needed("SKU001")

    assert needs_replenishment is False
    assert "库存充足" in reason


@pytest.mark.asyncio
async def test_check_replenishment_needed_not_found():
    mock_db = MagicMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()

    service = InventorySyncService(mock_db, mock_oms, mock_srm)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    needs_replenishment, reason = await service.check_replenishment_needed("SKU_NOT_EXIST")

    assert needs_replenishment is False
    assert "SKU不存在" in reason

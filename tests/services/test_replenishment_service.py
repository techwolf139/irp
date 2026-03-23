import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta
from irp.services.replenishment_service import ReplenishmentService
from irp.models.inventory import ReplenishmentTask


@pytest.mark.asyncio
async def test_check_and_create_replenishment_needed():
    mock_db = MagicMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    mock_srm = AsyncMock()
    mock_inventory_sync = AsyncMock()

    mock_inventory_sync.check_replenishment_needed = AsyncMock(
        return_value=(True, "可用库存50 < 补货点100")
    )

    mock_inventory = MagicMock()
    mock_inventory.reorder_qty = 200
    mock_inventory.lead_time_days = 7

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_inventory)
    mock_db.execute = AsyncMock(return_value=mock_result)

    service = ReplenishmentService(mock_db, mock_srm, mock_inventory_sync)
    created, message = await service.check_and_create_replenishment("SKU001")

    assert created is True
    assert "补货任务已创建" in message
    mock_db.add.assert_called_once()


@pytest.mark.asyncio
async def test_check_and_create_replenishment_not_needed():
    mock_db = MagicMock()
    mock_srm = AsyncMock()
    mock_inventory_sync = AsyncMock()

    mock_inventory_sync.check_replenishment_needed = AsyncMock(
        return_value=(False, "库存充足")
    )

    service = ReplenishmentService(mock_db, mock_srm, mock_inventory_sync)
    created, message = await service.check_and_create_replenishment("SKU001")

    assert created is False
    assert "库存充足" in message


@pytest.mark.asyncio
async def test_initiate_procurement():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()

    mock_srm = AsyncMock()
    mock_srm.get_price_comparison = AsyncMock(return_value={})
    mock_srm.create_purchase_requisition = AsyncMock(return_value="REQ001")

    mock_inventory_sync = AsyncMock()

    mock_task = MagicMock()
    mock_task.task_id = "RPT001"
    mock_task.sku_id = "SKU001"
    mock_task.qty = 100
    mock_task.supplier_id = "SUP001"
    mock_task.status = "待采购"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
    mock_db.execute = AsyncMock(return_value=mock_result)

    service = ReplenishmentService(mock_db, mock_srm, mock_inventory_sync)
    requisition_id = await service.initiate_procurement("RPT001")

    assert requisition_id == "REQ001"
    assert mock_task.status == "待人工确认"


@pytest.mark.asyncio
async def test_initiate_procurement_wrong_status():
    mock_db = MagicMock()
    mock_srm = AsyncMock()
    mock_inventory_sync = AsyncMock()

    mock_task = MagicMock()
    mock_task.task_id = "RPT001"
    mock_task.status = "采购中"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
    mock_db.execute = AsyncMock(return_value=mock_result)

    service = ReplenishmentService(mock_db, mock_srm, mock_inventory_sync)

    with pytest.raises(ValueError, match="任务状态错误"):
        await service.initiate_procurement("RPT001")


@pytest.mark.asyncio
async def test_approve_and_order():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()

    mock_srm = AsyncMock()
    mock_srm.confirm_purchase_order = AsyncMock(return_value="PO001")

    mock_inventory_sync = AsyncMock()

    mock_task = MagicMock()
    mock_task.task_id = "RPT001"
    mock_task.requisition_id = "REQ001"
    mock_task.status = "待人工确认"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_task)
    mock_db.execute = AsyncMock(return_value=mock_result)

    service = ReplenishmentService(mock_db, mock_srm, mock_inventory_sync)
    po_id = await service.approve_and_order("RPT001")

    assert po_id == "PO001"
    assert mock_task.status == "采购中"

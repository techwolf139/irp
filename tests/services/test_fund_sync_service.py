import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.fund_sync_service import FundSyncService


@pytest.mark.asyncio
async def test_get_dashboard():
    mock_db = AsyncMock()
    mock_pms = AsyncMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()

    service = FundSyncService(mock_db, mock_pms, mock_oms, mock_srm)

    mock_income_result = MagicMock()
    mock_income_result.scalar.return_value = 1000000.0
    mock_expense_result = MagicMock()
    mock_expense_result.scalar.return_value = 600000.0
    mock_breakdown_result = MagicMock()
    mock_breakdown_result.all.return_value = []

    mock_db.execute.side_effect = [
        mock_income_result,
        mock_expense_result,
        mock_breakdown_result
    ]

    dashboard = await service.get_dashboard()

    assert dashboard["total_income"] == 1000000.0
    assert dashboard["total_expense"] == 600000.0
    assert dashboard["net_flow"] == 400000.0


@pytest.mark.asyncio
async def test_get_dashboard_zero_values():
    mock_db = AsyncMock()
    mock_pms = AsyncMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()

    service = FundSyncService(mock_db, mock_pms, mock_oms, mock_srm)

    mock_income_result = MagicMock()
    mock_income_result.scalar.return_value = None
    mock_expense_result = MagicMock()
    mock_expense_result.scalar.return_value = None
    mock_breakdown_result = MagicMock()
    mock_breakdown_result.all.return_value = []

    mock_db.execute.side_effect = [
        mock_income_result,
        mock_expense_result,
        mock_breakdown_result
    ]

    dashboard = await service.get_dashboard()

    assert dashboard["total_income"] == 0
    assert dashboard["total_expense"] == 0
    assert dashboard["net_flow"] == 0


@pytest.mark.asyncio
async def test_sync_from_oms():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_pms = AsyncMock()
    mock_oms = AsyncMock()
    mock_srm = AsyncMock()

    mock_sale = MagicMock()
    mock_sale.sale_id = "SALE001"
    mock_sale.sale_date = "2024-03-01"
    mock_sale.amount = 50000.0
    mock_sale.project_id = "PRJ001"

    mock_oms.get_sales = AsyncMock(return_value=[mock_sale])

    service = FundSyncService(mock_db, mock_pms, mock_oms, mock_srm)
    await service.sync_from_oms("2024-01-01", "2024-12-31")

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

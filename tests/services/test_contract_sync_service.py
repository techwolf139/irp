import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.contract_sync_service import ContractSyncService
from irp.models.contract import ContractMaster


@pytest.mark.asyncio
async def test_link_pms_contract():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()

    mock_srm = AsyncMock()
    mock_pms = AsyncMock()

    service = ContractSyncService(mock_db, mock_srm, mock_pms)

    mock_parent = MagicMock()
    mock_parent.child_contract_ids = []
    mock_parent.supplier_id = "SUP001"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_parent)
    mock_db.execute = AsyncMock(return_value=mock_result)

    await service.link_pms_contract("SRM-CON001", "PMS-CON001")

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_link_pms_contract_no_parent():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()

    mock_srm = AsyncMock()
    mock_pms = AsyncMock()

    service = ContractSyncService(mock_db, mock_srm, mock_pms)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    await service.link_pms_contract("SRM-NONEXISTENT", "PMS-CON001")

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_sync_from_srm_creates_new_contract():
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    mock_srm = AsyncMock()
    mock_srm.get_contracts = AsyncMock(return_value=[])

    mock_pms = AsyncMock()

    service = ContractSyncService(mock_db, mock_srm, mock_pms)
    await service.sync_from_srm()

    mock_srm.get_contracts.assert_called_once()
    mock_db.commit.assert_called_once()

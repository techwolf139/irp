import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.rule_learning_service import RuleLearningService


@pytest.mark.asyncio
async def test_record_decision():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    service = RuleLearningService(mock_db)

    context = {
        "supplier_id": "SUP001",
        "supplier_risk_level": "低",
        "order_amount": 50000
    }

    result = await service.record_decision(context, "approve", "success")

    assert result is None


@pytest.mark.asyncio
async def test_check_and_create_rule():
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    mock_decisions = [
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
        MagicMock(decision="approve", context={}),
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_decisions
    mock_db.execute.return_value = mock_result

    service = RuleLearningService(mock_db)
    service.min_samples = 3
    service.confidence_threshold = 0.8

    result = await service.check_and_create_rule({"supplier_id": "SUP001"}, "approve")

    assert result is None


def test_extract_pattern():
    mock_db = MagicMock()
    service = RuleLearningService(mock_db)

    context = {
        "supplier_id": "SUP001",
        "supplier_risk_level": "低",
        "supplier_rating": 4.5,
        "order_amount_range": "50000-100000"
    }

    pattern = service.extract_pattern(context)

    assert pattern["supplier_risk_level"] == "低"
    assert pattern["supplier_rating"] == 4.5


def test_build_condition():
    mock_db = MagicMock()
    service = RuleLearningService(mock_db)

    pattern = {
        "supplier_risk_level": "低",
        "supplier_rating": 4.5
    }

    condition = service.build_condition(pattern)

    assert "低" in condition
    assert "4.5" in condition

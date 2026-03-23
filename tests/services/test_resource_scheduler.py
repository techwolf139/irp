import pytest
from unittest.mock import AsyncMock, MagicMock
from irp.services.resource_scheduler import ResourceScheduler
from irp.models.resource import TaskRequest


def test_analyze_task_features_human_oriented():
    scheduler = ResourceScheduler(None)

    task = MagicMock()
    task.features = {
        "need_judgment": 0.8,
        "need_creativity": 0.7,
        "data_intensive": 0.2,
        "repeatability": 0.1
    }

    analysis = scheduler.analyze_task_features(task)

    assert analysis["recommended_approach"] == "human"
    assert analysis["human_ratio"] > analysis["ai_ratio"]


def test_analyze_task_features_ai_oriented():
    scheduler = ResourceScheduler(None)

    task = MagicMock()
    task.features = {
        "need_judgment": 0.2,
        "need_creativity": 0.2,
        "data_intensive": 0.9,
        "repeatability": 0.8
    }

    analysis = scheduler.analyze_task_features(task)

    assert analysis["recommended_approach"] == "ai"
    assert analysis["ai_ratio"] > analysis["human_ratio"]


def test_analyze_task_features_balanced():
    scheduler = ResourceScheduler(None)

    task = MagicMock()
    task.features = {
        "need_judgment": 0.5,
        "need_creativity": 0.5,
        "data_intensive": 0.5,
        "repeatability": 0.5
    }

    analysis = scheduler.analyze_task_features(task)

    assert analysis["human_ratio"] == analysis["ai_ratio"]


@pytest.mark.asyncio
async def test_allocate_task_human_preferred():
    mock_db = AsyncMock()
    scheduler = ResourceScheduler(mock_db)

    mock_task = MagicMock()
    mock_task.task_id = "TASK001"
    mock_task.features = {
        "need_judgment": 0.8,
        "need_creativity": 0.6,
        "data_intensive": 0.3,
        "repeatability": 0.2
    }
    mock_task.constraints = {}
    mock_task.preferences = {}

    mock_human = MagicMock()
    mock_human.resource_id = "RES001"
    mock_human.name = "张三"
    mock_human.skills = ["Python"]

    mock_ai = MagicMock()
    mock_ai.resource_id = "AI001"
    mock_ai.name = "数据分析AI"

    async def mock_execute(query):
        result = MagicMock()
        if "human" in str(query):
            result.scalars.return_value.all.return_value = [mock_human]
        else:
            result.scalars.return_value.all.return_value = [mock_ai]
        return result

    mock_db.execute = mock_execute

    allocation = await scheduler.allocate_task(mock_task)

    assert allocation["task_id"] == "TASK001"
    assert allocation["human_allocation"] is not None
    assert allocation["human_allocation"]["name"] == "张三"
    assert allocation["ai_allocation"] is None


@pytest.mark.asyncio
async def test_allocate_task_no_resources():
    mock_db = AsyncMock()
    scheduler = ResourceScheduler(mock_db)

    mock_task = MagicMock()
    mock_task.task_id = "TASK002"
    mock_task.features = {"need_judgment": 0.5, "need_creativity": 0.5, "data_intensive": 0.5, "repeatability": 0.5}
    mock_task.constraints = {}
    mock_task.preferences = {}

    async def mock_execute(query):
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        return result

    mock_db.execute = mock_execute

    allocation = await scheduler.allocate_task(mock_task)

    assert allocation["confidence"] == 0.1
    assert "无可用资源" in allocation["reasoning"]

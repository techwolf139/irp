import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from irp.services.task_scheduler import TaskScheduler, PriorityEscalation, TaskPriority
from irp.models.resource import TaskRequest


def test_priority_escalation_p2_to_p1():
    task = MagicMock()
    task.status = "pending"
    task.priority = "P2"
    task.constraints = {"deadline": datetime.utcnow() - timedelta(hours=1)}

    result = PriorityEscalation.evaluate(task, datetime.utcnow())
    assert result == "P1"


def test_priority_escalation_p1_to_p0():
    task = MagicMock()
    task.status = "pending"
    task.priority = "P1"
    task.constraints = {"deadline": datetime.utcnow() - timedelta(minutes=20)}

    result = PriorityEscalation.evaluate(task, datetime.utcnow())
    assert result == "P0"


def test_priority_escalation_no_escalation():
    task = MagicMock()
    task.status = "pending"
    task.priority = "P2"
    task.constraints = {"deadline": datetime.utcnow() + timedelta(hours=5)}

    result = PriorityEscalation.evaluate(task, datetime.utcnow())
    assert result is None


def test_priority_escalation_not_pending():
    task = MagicMock()
    task.status = "allocated"
    task.priority = "P2"
    task.constraints = {"deadline": datetime.utcnow() - timedelta(hours=1)}

    result = PriorityEscalation.evaluate(task, datetime.utcnow())
    assert result is None


@pytest.mark.asyncio
async def test_submit_task_blocked():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    mock_scheduler = MagicMock()
    mock_rule_engine = MagicMock()
    mock_rule_engine.evaluate.return_value = {
        "blocked": True,
        "reason": "失信供应商禁止"
    }

    scheduler = TaskScheduler(mock_db, mock_scheduler, mock_rule_engine)

    task = MagicMock()
    task.task_id = "TASK001"
    task.priority = "P2"
    task.constraints = {}
    task.model_dump = MagicMock(return_value={})

    with pytest.raises(ValueError, match="任务被拦截"):
        await scheduler.submit_task(task)


@pytest.mark.asyncio
async def test_submit_task_success():
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.add = MagicMock()

    mock_scheduler = MagicMock()
    mock_rule_engine = MagicMock()
    mock_rule_engine.evaluate.return_value = {
        "blocked": False,
        "passed": True
    }

    scheduler = TaskScheduler(mock_db, mock_scheduler, mock_rule_engine)

    task = MagicMock()
    task.task_id = "TASK002"
    task.task_type = "测试任务"
    task.priority = "P2"
    task.constraints = {}
    task.status = "pending"
    task.model_dump = MagicMock(return_value={
        "task_id": "TASK002",
        "task_type": "测试任务",
        "priority": "P2",
        "constraints": {},
        "status": "pending"
    })

    task_id = await scheduler.submit_task(task)

    assert task_id == "TASK002"
    mock_db.add.assert_called_once()

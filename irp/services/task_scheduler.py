from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from irp.models.resource import TaskRequest


class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class PriorityEscalation:
    RULES = [
        {"trigger": "P2 + deadline < 2h + not_started", "action": "upgrade_to", "target": "P1"},
        {"trigger": "P1 + deadline < 30min + not_started", "action": "upgrade_to", "target": "P0"},
        {"trigger": "P0 + queued > 1h + no_assignment", "action": "notify_manager", "target": None},
    ]

    @classmethod
    def evaluate(cls, task: TaskRequest, current_time: datetime) -> Optional[str]:
        task_status: str = task.status or "pending"  # type: ignore
        if str(task_status) != "pending":  # type: ignore
            return None

        deadline = task.constraints.get("deadline") if task.constraints else None  # type: ignore
        time_until_deadline = (deadline - current_time).total_seconds() / 3600 if deadline else None  # type: ignore

        priority: str = task.priority or "P3"  # type: ignore
        if str(priority) == "P2":  # type: ignore
            if time_until_deadline is not None and time_until_deadline < 2:
                return "P1"
        elif str(priority) == "P1":  # type: ignore
            if time_until_deadline is not None and time_until_deadline < 0.5:
                return "P0"

        return None

        priority = task.priority if isinstance(task.priority, str) else ""
        if not priority or priority.startswith("Column"):
            priority = getattr(task, '_priority', None) or ""

        if priority == "P2" or "P2":
            if priority == "P2":
                return _check_deadline(task, current_time, 2, "P1")
        elif priority == "P1":
            return _check_deadline(task, current_time, 0.5, "P0")

        return None


def _check_deadline(task: TaskRequest, current_time: datetime, threshold_hours: float, target_priority: str) -> Optional[str]:
    """Helper function to check deadline and return escalation priority.
    用于检查任务截点时间并返回优先级提升建议。
    """
    deadline = task.constraints.get("deadline") if task.constraints and isinstance(task.constraints, dict) else None  # type: ignore
    if deadline and isinstance(deadline, datetime):  # type: ignore
        time_until_deadline = (deadline - current_time).total_seconds() / 3600  # type: ignore
        if 0 < time_until_deadline < threshold_hours:  # type: ignore
            return target_priority
    return None


class TaskScheduler:
    def __init__(self, db, resource_scheduler, rule_engine):
        self.db = db
        self.resource_scheduler = resource_scheduler
        self.rule_engine = rule_engine

    async def submit_task(self, task_request: TaskRequest) -> str:
        context = {"task": task_request.model_dump()}
        evaluation = self.rule_engine.evaluate(context)

        if evaluation.get("blocked", False):
            task_request.status = "blocked"  # type: ignore
            await self.db.commit()
            raise ValueError(f"任务被拦截：{evaluation.get('reason', 'Unknown')}")

        if not task_request.priority:  # type: ignore
            task_request.priority = "P2"  # type: ignore

        task_request.status = "pending"  # type: ignore

        self.db.add(task_request)
        await self.db.commit()

        return task_request.task_id or ""  # type: ignore

    async def process_pending_tasks(self):
        from sqlalchemy import select

        result = await self.db.execute(
            select(TaskRequest).where(TaskRequest.status == "pending")
        )
        pending_tasks = result.scalars().all()

        processed = []
        for task in pending_tasks:
            try:
                allocation = await self.resource_scheduler.allocate_task(task)
                task.status = "allocated"
                await self.db.commit()
                processed.append({"task_id": task.task_id, "allocation": allocation})
            except Exception as e:
                print(f"任务分配失败 {task.task_id}: {e}")

        return processed

    async def check_priority_escalation(self):
        from sqlalchemy import select

        current_time = datetime.utcnow()

        result = await self.db.execute(
            select(TaskRequest).where(TaskRequest.status == "pending")
        )
        pending_tasks = result.scalars().all()

        escalated = []
        for task in pending_tasks:
            new_priority = PriorityEscalation.evaluate(task, current_time)
            if new_priority:
                old_priority = task.priority
                task.priority = new_priority
                escalated.append({
                    "task_id": task.task_id,
                    "old_priority": old_priority,
                    "new_priority": new_priority
                })

        if escalated:
            await self.db.commit()

        return escalated

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
        if task.status != "pending":
            return None

        deadline = task.constraints.get("deadline") if task.constraints else None
        time_until_deadline = (deadline - current_time).total_seconds() / 3600 if deadline else None

        priority = task.priority

        if priority == "P2" and time_until_deadline is not None and time_until_deadline < 2:
            return "P1"

        if priority == "P1" and time_until_deadline is not None and time_until_deadline < 0.5:
            return "P0"

        return None


class TaskScheduler:
    def __init__(self, db, resource_scheduler, rule_engine):
        self.db = db
        self.resource_scheduler = resource_scheduler
        self.rule_engine = rule_engine

    async def submit_task(self, task_request: TaskRequest) -> str:
        context = {"task": task_request.model_dump()}
        evaluation = self.rule_engine.evaluate(context)

        if evaluation["blocked"]:
            task_request.status = "blocked"
            await self.db.commit()
            raise ValueError(f"任务被拦截: {evaluation['reason']}")

        if not task_request.priority:
            task_request.priority = "P2"

        task_request.status = "pending"

        self.db.add(task_request)
        await self.db.commit()

        return task_request.task_id

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

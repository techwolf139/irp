from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from irp.models.resource import HumanResource, TaskRequest


class ResourceScheduler:
    def __init__(self, db: AsyncSession):
        self.db = db

    def analyze_task_features(self, task_request: TaskRequest) -> dict:
        features = task_request.features or {}

        judgment_score = features.get("need_judgment", 0.5)
        creativity_score = features.get("need_creativity", 0.5)
        data_intensive_score = features.get("data_intensive", 0.5)
        repeatability_score = features.get("repeatability", 0.5)

        human_score = (
            judgment_score * 0.4 +
            creativity_score * 0.4 +
            (1 - data_intensive_score) * 0.1 +
            (1 - repeatability_score) * 0.1
        )

        ai_score = (
            data_intensive_score * 0.4 +
            repeatability_score * 0.4 +
            (1 - judgment_score) * 0.1 +
            (1 - creativity_score) * 0.1
        )

        total = human_score + ai_score
        human_ratio = human_score / total if total > 0 else 0.5
        ai_ratio = ai_score / total if total > 0 else 0.5

        return {
            "human_ratio": human_ratio,
            "ai_ratio": ai_ratio,
            "recommended_approach": "human" if human_ratio > ai_ratio else "ai"
        }

    async def find_matching_resources(
        self, task_request: TaskRequest, resource_type: str
    ) -> List[HumanResource]:
        constraints = task_request.constraints or {}
        required_skills = constraints.get("required_skills", [])

        query = select(HumanResource).where(
            HumanResource.type == resource_type,
            HumanResource.status == "available"
        )

        result = await self.db.execute(query)
        all_resources = result.scalars().all()

        if required_skills and resource_type == "human":
            matched = []
            for resource in all_resources:
                resource_skills = resource.skills or []
                if any(skill in resource_skills for skill in required_skills):
                    matched.append(resource)
            return matched

        return list(all_resources)

    async def allocate_task(self, task_request: TaskRequest) -> dict:
        analysis = self.analyze_task_features(task_request)

        human_resources = await self.find_matching_resources(task_request, "human")
        ai_resources = await self.find_matching_resources(task_request, "ai")

        human_ratio = analysis["human_ratio"]
        ai_ratio = analysis["ai_ratio"]

        allocation = {
            "task_id": task_request.task_id,
            "analysis": analysis,
            "human_allocation": None,
            "ai_allocation": None,
            "confidence": 0.7 if (human_resources and ai_resources) else 0.4,
            "reasoning": ""
        }

        if human_resources and human_ratio > 0.3:
            allocation["human_allocation"] = {
                "resource_id": human_resources[0].resource_id,
                "name": human_resources[0].name,
                "ratio": human_ratio,
                "time_estimate_hours": 4
            }

        if ai_resources and ai_ratio > 0.3:
            allocation["ai_allocation"] = {
                "resource_id": ai_resources[0].resource_id,
                "name": ai_resources[0].name,
                "ratio": ai_ratio,
                "time_estimate_hours": 1
            }

        if allocation["human_allocation"] and allocation["ai_allocation"]:
            allocation["reasoning"] = "混合方案：AI处理数据，人力处理创意和判断"
        elif allocation["human_allocation"]:
            allocation["reasoning"] = f"人力方案：推荐 {human_resources[0].name}"
        elif allocation["ai_allocation"]:
            allocation["reasoning"] = f"AI方案：{ai_resources[0].name} 自动处理"
        else:
            allocation["reasoning"] = "无可用资源，请人工分配"
            allocation["confidence"] = 0.1

        return allocation

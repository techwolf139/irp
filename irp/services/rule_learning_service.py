from datetime import datetime
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class RuleLearningService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.min_samples = 5
        self.confidence_threshold = 0.7

    async def record_decision(self, context: dict, decision: str, outcome: str):
        pass

    async def check_and_create_rule(self, context: dict, decision: str):
        pass

    async def find_similar_decisions(self, context: dict) -> list:
        return []

    def extract_pattern(self, context: dict) -> dict:
        return {
            "supplier_risk_level": context.get("supplier_risk_level"),
            "supplier_rating": context.get("supplier_rating"),
            "order_amount_range": context.get("order_amount_range"),
            "decision_trigger": context.get("decision_trigger")
        }

    async def approve_rule(self, rule_id: str):
        pass

    def build_condition(self, pattern: dict) -> str:
        conditions = []
        if pattern.get("supplier_risk_level"):
            conditions.append(f"supplier.get('risk_level') == '{pattern['supplier_risk_level']}'")
        if pattern.get("supplier_rating"):
            conditions.append(f"supplier.get('rating', 0) >= {pattern['supplier_rating']}")
        return " and ".join(conditions) if conditions else "true"

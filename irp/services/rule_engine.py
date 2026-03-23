from typing import Any
from pydantic import BaseModel
from enum import Enum


class RuleType(str, Enum):
    HARD_CONSTRAINT = "hard_constraint"
    SOFT_RULE = "soft_rule"
    LEARNED_RULE = "learned_rule"


class RuleAction(str, Enum):
    BLOCK = "block"
    FORCE = "force"
    PREFER = "prefer"
    AVOID = "avoid"


class Rule(BaseModel):
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    condition: str
    action: RuleAction
    action_params: dict = {}
    weight: float = 0.5
    priority: int = 50
    enabled: bool = True
    source: str = "system"


class RuleEngine:
    def __init__(self):
        self.hard_constraints: list[Rule] = []
        self.soft_rules: list[Rule] = []
        self.learned_rules: list[Rule] = []

    def add_rule(self, rule: Rule):
        if rule.rule_type == RuleType.HARD_CONSTRAINT:
            self.hard_constraints.append(rule)
        elif rule.rule_type == RuleType.SOFT_RULE:
            self.soft_rules.append(rule)
        else:
            self.learned_rules.append(rule)

    def evaluate_condition(self, condition: str, context: dict) -> bool:
        try:
            safe_globals = {"true": True, "false": False, "null": None}
            return eval(condition, safe_globals, context)
        except Exception:
            return False

    def evaluate_hard_constraints(self, context: dict) -> tuple[bool, list[str]]:
        failed_rules = []

        for rule in self.hard_constraints:
            if not rule.enabled:
                continue

            if self.evaluate_condition(rule.condition, context):
                failed_rules.append(rule.name)

        return len(failed_rules) == 0, failed_rules

    def evaluate_soft_rules(self, context: dict) -> tuple[list[Rule], float]:
        matched_rules = []
        total_weight = 0.0

        for rule in self.soft_rules:
            if not rule.enabled:
                continue

            if self.evaluate_condition(rule.condition, context):
                matched_rules.append(rule)
                weight = rule.weight if rule.action == RuleAction.PREFER else -rule.weight
                total_weight += weight

        return matched_rules, total_weight

    def evaluate(self, context: dict) -> dict:
        hard_passed, failed_hard = self.evaluate_hard_constraints(context)

        if not hard_passed:
            return {
                "passed": False,
                "blocked": True,
                "reason": f"硬约束拦截: {', '.join(failed_hard)}",
                "recommendation": None,
                "confidence": 1.0
            }

        matched_soft, soft_score = self.evaluate_soft_rules(context)

        matched_learned, learned_score = self.evaluate_soft_rules(context)

        final_score = soft_score + learned_score

        if final_score > 0.3:
            recommendation = "推荐"
            confidence = 0.7
        elif final_score < -0.3:
            recommendation = "不推荐"
            confidence = 0.7
        else:
            recommendation = "需要人工判断"
            confidence = 0.4

        return {
            "passed": True,
            "blocked": False,
            "reason": f"软规则得分: {final_score:.2f}",
            "matched_rules": [r.name for r in matched_soft],
            "recommendation": recommendation,
            "confidence": confidence
        }

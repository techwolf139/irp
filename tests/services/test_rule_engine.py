import pytest
from irp.services.rule_engine import RuleEngine, Rule, RuleType, RuleAction


def test_hard_constraint_block():
    engine = RuleEngine()

    rule = Rule(
        rule_id="HC001",
        name="失信供应商禁止",
        description="失信供应商禁止合作",
        rule_type=RuleType.HARD_CONSTRAINT,
        condition="supplier.get('is_discredited', False) == True",
        action=RuleAction.BLOCK,
        priority=100
    )
    engine.add_rule(rule)

    context = {"supplier": {"is_discredited": True}}
    result = engine.evaluate(context)

    assert result["passed"] is False
    assert result["blocked"] is True
    assert "失信供应商禁止" in result["reason"]


def test_soft_rule_prefer():
    engine = RuleEngine()

    rule = Rule(
        rule_id="SR001",
        name="优先历史合作供应商",
        description="合作次数>5的供应商优先",
        rule_type=RuleType.SOFT_RULE,
        condition="supplier.get('cooperation_count', 0) > 5",
        action=RuleAction.PREFER,
        weight=0.3
    )
    engine.add_rule(rule)

    context = {"supplier": {"cooperation_count": 10}}
    result = engine.evaluate(context)

    assert result["passed"] is True
    assert "优先历史合作供应商" in result["matched_rules"]


def test_soft_rule_avoid():
    engine = RuleEngine()

    rule = Rule(
        rule_id="SR002",
        name="避免高风险供应商",
        description="风险评分>80的供应商降低优先级",
        rule_type=RuleType.SOFT_RULE,
        condition="supplier.get('risk_score', 0) > 80",
        action=RuleAction.AVOID,
        weight=0.4
    )
    engine.add_rule(rule)

    context = {"supplier": {"risk_score": 85}}
    result = engine.evaluate(context)

    assert result["passed"] is True
    assert "避免高风险供应商" in result["matched_rules"]


def test_no_rules():
    engine = RuleEngine()

    context = {"supplier": {"risk_score": 50}}
    result = engine.evaluate(context)

    assert result["passed"] is True
    assert result["blocked"] is False
    assert result["recommendation"] == "需要人工判断"


def test_multiple_soft_rules():
    engine = RuleEngine()

    rule1 = Rule(
        rule_id="SR001",
        name="优先高质量供应商",
        description="rating >= 4.0",
        rule_type=RuleType.SOFT_RULE,
        condition="supplier.get('rating', 0) >= 4.0",
        action=RuleAction.PREFER,
        weight=0.3
    )
    rule2 = Rule(
        rule_id="SR002",
        name="避免新供应商",
        description="cooperation_count < 3",
        rule_type=RuleType.SOFT_RULE,
        condition="supplier.get('cooperation_count', 0) < 3",
        action=RuleAction.AVOID,
        weight=0.2
    )
    engine.add_rule(rule1)
    engine.add_rule(rule2)

    context = {"supplier": {"rating": 4.5, "cooperation_count": 10}}
    result = engine.evaluate(context)

    assert result["passed"] is True
    assert len(result["matched_rules"]) == 1


def test_hard_constraint_pass():
    engine = RuleEngine()

    rule = Rule(
        rule_id="HC001",
        name="失信供应商禁止",
        description="失信供应商禁止合作",
        rule_type=RuleType.HARD_CONSTRAINT,
        condition="supplier.get('is_discredited', False) == True",
        action=RuleAction.BLOCK
    )
    engine.add_rule(rule)

    context = {"supplier": {"is_discredited": False}}
    result = engine.evaluate(context)

    assert result["passed"] is True

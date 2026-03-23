import pytest
from irp.models.resource import HumanResource, TaskRequest


def test_human_resource_creation():
    resource = HumanResource(
        resource_id="RES001",
        type="human",
        name="张三",
        skills=["Python", "项目管理"],
        availability=0.8,
        department="研发部",
        status="available"
    )
    assert resource.name == "张三"
    assert "Python" in resource.skills


def test_human_resource_full_fields():
    resource = HumanResource(
        resource_id="RES002",
        type="human",
        name="李四",
        owner="PMS",
        owner_id="PMS001",
        skills=["Java", "架构设计"],
        availability=0.5,
        current_projects=["PRJ001"],
        department="研发部",
        role="高级工程师",
        preferred_task_types=["backend", "api"],
        excluded_tasks=["frontend"],
        status="busy"
    )
    assert resource.availability == 0.5
    assert resource.role == "高级工程师"
    assert resource.status == "busy"


def test_ai_resource_creation():
    resource = HumanResource(
        resource_id="AI001",
        type="ai",
        name="数据分析AI",
        skill_packages=["数据分析", "报表生成"],
        capability_level="高级",
        cost_per_call=0.01,
        status="available"
    )
    assert resource.type == "ai"
    assert resource.cost_per_call == 0.01


def test_task_request_creation():
    task = TaskRequest(
        task_id="TASK001",
        task_type="数据分析",
        features={"need_judgment": 0.3, "need_creativity": 0.2},
        constraints={"max_cost": 1000},
        preferences={"prefer_ai": True},
        priority="P1",
        status="pending"
    )
    assert task.task_id == "TASK001"
    assert task.priority == "P1"


def test_task_request_full_fields():
    task = TaskRequest(
        task_id="TASK002",
        task_type="文档撰写",
        features={"need_judgment": 0.7, "need_creativity": 0.9, "data_intensive": 0.1},
        constraints={"max_cost": 500, "required_skills": ["写作"]},
        preferences={"prefer_human": True},
        priority="P2",
        status="allocated"
    )
    assert task.features["need_creativity"] == 0.9
    assert task.constraints["required_skills"] == ["写作"]

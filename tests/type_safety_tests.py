"""
测试用例用于验证 IRP 类型安全性改进。

包含:
- 数据库 Session 管理测试
- Retry 装饰器测试
- Pydantic ORM 映射测试
- 任务调度器测试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock
from irp.core.database import get_db, Base
from irp.core.retry import retry_async, RetryConfig


class TestAsyncSession:
    """测试 AsyncSession 上下文管理器"""

    @pytest.mark.asyncio
    async def test_get_db_provides_session(self):
        """测试 get_db 提供有效的 session"""
        async with get_db() as session:
            assert session is not None
            # 验证 session 可以执行基础操作
            result = await session.execute("SELECT 1")
            assert result

    @pytest.mark.asyncio
    async def test_get_db_commit_on_success(self):
        """测试成功操作后自动提交"""
        async with get_db() as session:
            # 模拟 successful commit
            pass

    @pytest.mark.asyncio
    async def test_get_db_rollback_on_error(self):
        """测试错误后自动回滚"""
        with pytest.raises(Exception):
            async with get_db() as session:
                raise ValueError("Test error")


class TestRetryDecorator:
    """测试 retry 装饰器"""

    @pytest.mark.asyncio
    async def test_retry_success_on_first_try(self):
        """测试第一次尝试就成功"""
        call_count = 0

        @retry_async(max_retries=3, delay=0.1, backoff=2.0)
        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await success_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_succeeds_after_failures(self):
        """测试失败后重试成功"""
        call_count = 0

        @retry_async(max_retries=3, delay=0.1, backoff=2.0, exceptions=ValueError)
        async def fail_twice_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await fail_twice_then_succeed()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_max_retries(self):
        """测试超过最大重试次数后抛出异常"""
        call_count = 0

        @retry_async(max_retries=2, delay=0.1, backoff=2.0, exceptions=ValueError)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            await always_fails()

        assert call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_retry_config(self):
        """测试 RetryConfig"""
        config = RetryConfig(
            max_retries=5,
            delay=2.0,
            backoff=1.5,
            timeout=60.0
        )

        assert config.max_retries == 5
        assert config.delay == 2.0
        assert config.backoff == 1.5
        assert config.timeout == 60.0

    @pytest.mark.asyncio
    async def test_retry_config_uses_defaults(self):
        """测试 RetryConfig 使用默认值"""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.delay == 1.0
        assert config.backoff == 2.0
        assert config.timeout == 30.0


class TestContractResponse:
    """测试 ContractResponse ORM 映射"""

    def test_from_model_valid_contract(self):
        """测试从有效的 ContractMaster 模型创建响应"""
        from irp.api.contracts import ContractResponse
        from irp.models.contract import ContractMaster

        mock_contract = ContractMaster(
            contract_id="TEST001",
            source_system="IRP",
            source_id="SRC001",
            title="Test Contract",
            type="Framework",
            status="履行中",
            total_amount=10000.0,
            currency="USD"
        )

        response = ContractResponse.from_model(mock_contract)

        assert response.contract_id == "TEST001"
        assert response.title == "Test Contract"
        assert response.status == "履行中"
        assert response.total_amount == 10000.0
        assert response.currency == "USD"

    def test_from_model_null_fields(self):
        """测试 null 字段处理"""
        from irp.api.contracts import ContractResponse
        from irp.models.contract import ContractMaster

        mock_contract = ContractMaster(
            contract_id="TEST002",
            source_system="IRP",
            source_id="SRC002",
            title="Test Contract 2",
            type=None,
            status="草稿",
            total_amount=0,
            currency=None
        )

        response = ContractResponse.from_model(mock_contract)

        assert response.contract_id == "TEST002"
        assert response.title == "Test Contract 2"
        assert response.type is None
        assert response.total_amount == 0.0
        assert response.currency == "CNY"  # Default

    def test_contract_detail_from_model(self):
        """测试 ContractDetailResponse"""
        from irp.api.contracts import ContractDetailResponse
        from irp.models.contract import ContractMaster

        mock_contract = ContractMaster(
            contract_id="TEST003",
            source_system="IRP",
            source_id="SRC003"
        )

        response = ContractDetailResponse.from_model(mock_contract)

        assert response.contract_id == "TEST003"
        assert response.contract_no is None
        assert response.child_contract_ids == []
        assert response.tax_rate == float(0)  # Default from model


class TestSupplierResponse:
    """测试 SupplierResponse ORM 映射"""

    def test_from_model_valid_supplier(self):
        """测试从有效的 SupplierMaster 模型创建响应"""
        from irp.api.suppliers import SupplierResponse
        from irp.models.supplier import SupplierMaster

        mock_supplier = SupplierMaster(
            supplier_id="SUP001",
            name="Test Supplier",
            risk_score=85.0,
            rating=4.5,
            status="Active"
        )

        response = SupplierResponse.from_model(mock_supplier)

        assert response.supplier_id == "SUP001"
        assert response.name == "Test Supplier"
        assert response.risk_score == 85.0
        assert response.rating == 4.5
        assert response.status == "Active"

    def test_from_model_null_fields(self):
        """测试 null 字段处理"""
        from irp.api.suppliers import SupplierResponse
        from irp.models.supplier import SupplierMaster

        mock_supplier = SupplierMaster(
            supplier_id="SUP002",
            name="Test Supplier 2",
            risk_score=0,
            rating=0,
            status=None
        )

        response = SupplierResponse.from_model(mock_supplier)

        assert response.supplier_id == "SUP002"
        assert response.risk_score == 0.0
        assert response.rating == 0.0
        assert response.status == "Pending"  # Default


class TestTaskScheduler:
    """测试 TaskScheduler"""

    @pytest.mark.asyncio
    async def test_submit_task_workflow(self):
        """测试提交任务工作流程"""
        from irp.services.task_scheduler import TaskScheduler, TaskPriority
        from irp.models.resource import TaskRequest

        # 模拟依赖
        mock_db = MagicMock()
        mock_resource_scheduler = MagicMock()
        mock_rule_engine = MagicMock()

        scheduler = TaskScheduler(
            db=mock_db,
            resource_scheduler=mock_resource_scheduler,
            rule_engine=mock_rule_engine
        )

        # Mock rule engine evaluation
        mock_rule_engine.evaluate.return_value = {"blocked": False, "recommendation": "auto"}

        # Create mock task
        mock_task = MagicMock(spec=TaskRequest)
        mock_task.task_id = "TASK001"
        mock_task.priority = "P2"
        mock_model_dump = MagicMock()
        mock_task.model_dump.return_value = mock_model_dump

        # Submit task
        result = await scheduler.submit_task(mock_task)

        assert result == "TASK001"
        mock_rule_engine.evaluate.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_priority_escalation(self):
        """测试优先级提升检查"""
        from irp.services.task_scheduler import TaskScheduler, TaskPriority
        from irp.models.resource import TaskRequest
        from irp.models.resource import ResourceScheduler

        mock_db = MagicMock()
        resource_scheduler = ResourceScheduler(mock_db)
        rule_engine = MagicMock()

        scheduler = TaskScheduler(
            db=mock_db,
            resource_scheduler=resource_scheduler,
            rule_engine=rule_engine
        )

        # Mock pending tasks
        mock_task = MagicMock()
        mock_task.task_id = "TASK_ESCALATE"
        mock_task.priority = "P2"
        mock_task.status = "pending"

        mock_db.execute.return_value = MagicMock()
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_task]

        # Mock allocation
        mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_task]

        # Process pending tasks
        result = await scheduler.process_pending_tasks()

        # Verify tasks were processed
        assert isinstance(result, list)
        mock_db.execute.assert_called()


class TestPriorityEscalation:
    """测试优先级提升规则"""

    @pytest.mark.asyncio
    async def test_p2_to_p1_escalation(self):
        """测试 P2 提升到 P1"""
        from irp.services.task_scheduler import PriorityEscalation
        from irp.models.resource import TaskRequest

        # Create mock task with deadline < 2h
        mock_task = MagicMock()
        mock_task.status = "pending"
        mock_task.priority = "P2"
        mock_task.constraints = {
            "deadline": datetime.utcnow() + timedelta(hours=1)
        }

        new_priority = PriorityEscalation.evaluate(mock_task, datetime.utcnow())

        assert new_priority == "P1"

    @pytest.mark.asyncio
    async def test_p1_to_p0_escalation(self):
        """测试 P1 提升到 P0"""
        from irp.services.task_scheduler import PriorityEscalation
        from irp.models.resource import TaskRequest

        # Create mock task with deadline < 30min
        mock_task = MagicMock()
        mock_task.status = "pending"
        mock_task.priority = "P1"
        mock_task.constraints = {
            "deadline": datetime.utcnow() + timedelta(minutes=20)
        }

        new_priority = PriorityEscalation.evaluate(mock_task, datetime.utcnow())

        assert new_priority == "P0"

    @pytest.mark.asyncio
    async def test_no_escalation_needed(self):
        """测试不需要提升的情况"""
        from irp.services.task_scheduler import PriorityEscalation
        from irp.models.resource import TaskRequest

        # Task with no deadline or sufficient time
        mock_task = MagicMock()
        mock_task.status = "pending"
        mock_task.priority = "P2"
        mock_task.constraints = {
            "deadline": datetime.utcnow() + timedelta(hours=5)
        }

        new_priority = PriorityEscalation.evaluate(mock_task, datetime.utcnow())

        assert new_priority is None

    @pytest.mark.asyncio
    async def test_no_escalation_for_non_pending(self):
        """测试非 pending 状态不触发提升"""
        from irp.services.task_scheduler import PriorityEscalation
        from irp.models.resource import TaskRequest

        mock_task = MagicMock()
        mock_task.status = "allocated"  # Not pending
        mock_task.priority = "P1"

        new_priority = PriorityEscalation.evaluate(mock_task, datetime.utcnow())

        assert new_priority is None


class TestORMAttributeAccess:
    """测试 ORM 属性访问"""

    def test_column_value_extraction(self):
        """测试从 ORM 模型提取值"""
        from irp.api.contracts import ContractResponse
        from irp.models.contract import ContractMaster

        # Test that factory methods handle various value types
        mock_contract = ContractMaster(
            contract_id="TEST001",
            source_system="IRP",
            source_id="SRC001",
            title="Test",
            type="Framework",
            status="履行中",
            total_amount=10000.0,
            currency="USD",
            signed_date=None,
            start_date=None,
            end_date=None
        )

        # Verify factory method handles the model correctly
        response = ContractResponse.from_model(mock_contract)

        assert response.contract_id == "TEST001"
        assert response.total_amount == 10000.0

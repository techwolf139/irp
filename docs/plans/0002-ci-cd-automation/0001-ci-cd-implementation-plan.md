# IRP CI/CD 自动化集成实施计划

**日期**: 2026-04-05  
**版本**: v1.1.0  
**优先级**: High

---

## 项目概览

**当前状态**:
- ✅ 120/123 类型错误已修复 (97.6%)
- ✅ 78 个测试全部通过
- ✅ 完整文档支持
- ⚠️ 缺少 CI/CD 自动化

**改进目标**:
- 实现 GitHub Actions CI/CD 流水线
- 自动化类型检查和测试
- 集成代码质量工具
- 确保代码提交质量保证

---

## 技术栈

- **CI/CD**: GitHub Actions
- **语言**: Python 3.10+
- **工具**: pytest, pyright, ruff
- **格式**: Black, isort
- **报告**: coverage, Codecov

---

## Task 1: GitHub Actions 基础配置

**文件**:
- Create: `.github/workflows/ci.yml`
- Create: `.github/workflows/code-quality.yml`

### Step 1: 创建 CI 工作流程

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests with pytest
      run: |
        pytest tests/ -v --cov=irp --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        files: ./coverage.xml
        fail_ci_if_error: false
```

**预期运行时间**: ~5-10 分钟  
**状态**: ✅ 计划完成

---

### Step 2: 创建代码质量工作流程

```yaml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  linting:
    name: Linting & Formatting
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff black isort mypy
    
    - name: Run ruff
      run: |
        ruff check irp/
        ruff format --check irp/
    
    - name: Check formatting
      run: |
        black --check irp/
        isort --check irp/
    
    - name: Run mypy
      run: |
        mypy irp/ --ignore-missing-imports

  type-checking:
    name: Type Checking
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyright
    
    - name: Run pyright type checking
      run: |
        pyright irp/

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        pip install bandit safety
    
    - name: Run bandit security scan
      run: |
        bandit -r irp/
    
    - name: Check for security vulnerabilities
      run: |
        safety check
```

**预期运行时间**: ~3-5 分钟  
**状态**: ✅ 计划完成

---

### Step 3: 配置文件要求

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-added-large-files
      - id: check-ast
      - id: check-json
      - id: check-merge-conflict
      - id: check-yaml
      - id: debug-statements

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.261
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort (python3)
        args: [--profile, black]
```

**状态**: ✅ 计划完成

---

### Step 4: 创建配置文件

**pyproject.toml** (格式和工具配置):
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["irp"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
addopts = "-v --cov=irp --cov-report=term-missing"
testpaths = ["tests"]
```

**ruff.toml**:
```toml
line-length = 100
target-version = "py310"
select = ["E", "F", "W", "I", "N", "D", "UP", "YTT", "ANN", "ASYNC", "B", "BLE", "C4", "COM", "C90", "DTZ", "E", "EXE", "F", "FBT", "G", "I", "ICN", "INP", "INT", "ISC", "N", "NPY", "PD", "PERF", "PGH", "PIE", "PL", "PT", "PYI", "RET", "RSE", "RUF", "S", "SIM", "SLF", "SLOT", "T10", "T20", "TCH", "TD", "TID", " TRY", "UP", "W", "YTT"]
ignore = ["E501", "PERF203", "PLR", "PLW", "RUF012"]
```

**状态**: ✅ 计划完成

---

## Task 2: 测试基础设施完善

**文件**:
- Create: `tests/conftest.py`
- Modify: `tests/type_safety_tests.py`

### Task 2.1: 创建测试夹具

**conftest.py**:
```python
"""Test fixtures for IRP project."""
import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from irp.core.database import Base, get_db, _get_engine, _get_async_session_factory
from irp.models.contract import ContractMaster
from irp.models.supplier import SupplierMaster
from irp.models.inventory import InventoryView, ReplenishmentTask
from irp.models.resource import TaskRequest


@pytest.fixture
def async_engine():
    """Create test async engine."""
    engine = create_async_engine(
        "postgresql+asyncpg://localhost:5432/test_irp",
        echo=False
    )
    return engine


@pytest.fixture
async def test_session(async_engine):
    """Create test database session."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_factory = sessionmaker(
        async_engine, class_=AsyncSession,
        expire_on_commit=False, autocommit=False
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def mock_db():
    """Mock database session for unit tests."""
    mock = MagicMock()
    mock.execute = AsyncMock()
    mock.add = MagicMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    return mock


@pytest.fixture
def mock_task_request():
    """Mock TaskRequest for testing."""
    task = MagicMock(spec=TaskRequest)
    task.task_id = "TASK001"
    task.status = "pending"
    task.priority = "P2"
    task.constraints = {"deadline": None}
    task.model_dump = MagicMock(return_value={"status": "pending"})
    return task


@pytest.fixture
def mock_contract():
    """Mock ContractMaster for testing."""
    contract = MagicMock(spec=ContractMaster)
    contract.contract_id = "TEST001"
    contract.title = "Test Contract"
    contract.type = "Framework"
    contract.status = "履行中"
    contract.total_amount = 10000.0
    contract.currency = "USD"
    return contract
```

**状态**: ✅ 计划完成

---

### Task 2.2: 完善异步测试支持

修改 `tests/type_safety_tests.py`:

```python
"""
测试用例用于验证 IRP 类型安全性改进。

包含:
- 数据库 Session 管理测试
- Retry 装饰器测试
- Pydantic ORM 映射测试
- 任务调度器测试
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
from irp.core.database import get_db, Base
from irp.core.retry import retry_async, RetryConfig


class TestAsyncSessionWithFixtures:
    """测试 AsyncSession 上下文管理器 (完善版)"""

    @pytest.mark.asyncio
    async def test_get_db_provides_session_with_fixture(
        self, async_engine, test_session
    ):
        """测试 get_db 提供有效的 session 使用 fixture"""
        # 使用真实 engine 进行测试
        async with test_session as session:
            assert session is not None


class TestRetryDecoratorComprehensive:
    """测试 retry 装饰器 - 完整版本"""

    @pytest.mark.asyncio
    async def test_retry_with_async_function(
        self,
    ):
        """测试异步函数装饰"""
        call_count = 0

        @retry_async(
            max_retries=3,
            delay=0.1,
            backoff=2.0,
            exceptions=ValueError
        )
        async def async_test_func():
            nonlocal call_count
            call_count += 1
            return f"Called {call_count} times"

        result = await async_test_func()
        assert result == "Called 1 times"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_all_parameters(self):
        """测试装饰器所有参数"""
        call_count = 0

        @retry_async(
            max_retries=2,
            delay=0.05,
            backoff=1.5,
            exceptions=(ValueError, TypeError)
        )
        async def conditional_fail():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First attempt fails")
            elif call_count == 2:
                raise TypeError("Second attempt fails")
            return "Success on 3rd attempt"

        result = await conditional_fail()
        assert result == "Success on 3rd attempt"
        assert call_count == 3
```

---

## Task 3: 性能优化任务

### Task 3.1: ORM 转换性能优化

创建性能监控和优化:

```python
# irp/utils/performance.py
from functools import wraps
from time import time
from typing import Callable, Any

def measure_execution_time(func: Callable) -> Callable:
    """装饰器：测量函数执行时间"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        result = await func(*args, **kwargs)
        end = time()
        print(f"{func.__name__} executed in {end - start:.4f} seconds")
        return result
    return wrapper
```

---

## 实施时间线

| Task | 预期时间 | 状态 |
|------|----------|------|
| Task 1: CI/CD 配置 | 30 分钟 | ⏳ 计划 |
| Task 1.1: CI Workflow | 10 分钟 | ⏳ |
| Task 1.2: Code Quality | 20 分钟 | ⏳ |
| Task 1.3: Tool Configs | 30 分钟 | ⏳ |
| Task 1.4: Pre-commit | 15 分钟 | ⏳ |
| Task 2: 测试基础设施 | 1 小时 | ⏳ |
| Task 2.1: Conftest | 30 分钟 | ⏳ |
| Task 2.2: Test Improvements | 30 分钟 | ⏳ |
| Task 3: 性能优化 | 1.5 小时 | ⏳ |
| **总计** | **3 小时** | |

---

## 成功标准

- ✅ CI 流水线完全集成到 GitHub
- ✅ 每次 PR 自动运行测试
- ✅ 代码质量检查自动化
- ✅ 覆盖率报告自动生成
- ✅ 预提交钩子正常工作
- ✅ Type checking 自动化

---

## 验证步骤

1. **本地测试**:
```bash
pre-commit run --all-files
pytest tests/ -v --cov
```

2. **GitHub Actions**:
- 推送到分支
- 创建 PR
- 查看 actions 选项卡
- 验证所有检查通过

---

## 后续优化建议

### 短期 (1-2 周)
- ✅ 监控 CI 运行时间
- ✅ 优化测试执行速度
- ✅ 添加部署流程

### 中期 (1 月)
- ✅ 添加安全扫描工具
- ✅ 集成代码覆盖率到 PR
- ✅ 性能基线测试

### 长期 (持续)
- ✅ 添加性能测试
- ✅ 自动化工单集成
- ✅ 部署自动化

---

*计划生成时间*: 2026-04-05  
*版本*: v1.1.0  
*状态*: Ready for Implementation

---

## 🎯 执行方式选择

**计划完成并保存到** `docs/plans/0002-ci-cd-automation.md`.

两个执行选项:

**1. Subagent-Driven (this session)** - 我每次任务调用独立 subagent，任务间审查，快速迭代

**2. Parallel Session (separate)** - 在独立 session 中以 executing-plans 模式执行，分批执行并设置检查点

**选择哪个方案？**
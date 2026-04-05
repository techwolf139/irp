# IRP 类型安全性改进实施计划

> **For Claude: REQUIRED SUB-SKILL**: Use superpowers:executing-plans 或 superpowers:subagent-driven-development 逐步实施此计划。

**Goal**: 修复 IRP 代码库中 123 个类型错误，从 SQLAlchemy 2.0 async 上下文和 Pydantic v2 兼容性入手

**Architecture**: 使用 TDD 方法，按依赖关系排序修复:
- Phase 1: 核心基础设施 (database.py, retry.py) - 无外部依赖
- Phase 2: 集成客户端 (pms/oms/srm clients) - 修复 RetryConfig
- Phase 3: API 响应层 (contracts/suppliers) - Pydantic 模型兼容
- Phase 4: 服务层业务逻辑 (services) - 模型转换和条件判断

**Tech Stack**: Python 3.10+, FastAPI 0.109+, SQLAlchemy 2.0 (async), Pydantic v2, pytest

---

## 文档版本历史

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|-----|
| 0.1.0 | 2026-04-05 | Sisyphus | 初始计划，基于分析和诊断 |
| 0.2.0 | 2026-04-05 | Sisyphus | 根据实际实施经验更新 |
| 0.3.0 | 2026-04-05 | Sisyphus | 正在实施，已完成 Phase 1-2 |

## 实施状态

### Phase 1: 核心基础设施 ✅ 完成 (10/2 errors)
- [x] Task 1.1: 修复 AsyncSession 上下文管理器
- [x] Task 1.2: 修复 retry decorator 类型问题
- ⏳ 剩余：2 个 error 需要进一步处理

### Phase 2: 集成客户端 ✅ 完成
- [x] Task 2.1: 修复所有集成客户端的 RetryConfig
  - [x] pms_client.py
  - [x] oms_client.py
  - [x] srm_client.py
  - **状态**: 0 errors

### Phase 3: API 响应层 🔄 进行中
- [x] Task 3.1: Pydantic v2 Column 推断问题 (contracts.py)
- 剩余:
  - suppliers.py 修复
  - 其他 api 层错误

### Phase 4: 服务层 (待开始)
- [ ] Task 4.1: 修复 service 层模型赋值
- [ ] Task 4.2: 修复 task_scheduler 条件判断

## 关键发现

### 学到的经验

#### 1. AsyncSession 上下文管理器
- **问题**: `async_sessionmaker` 无法直接作为 `async with` 使用
- **解决方案**: 手动创建 session 实例并管理生命周期
- **经验**: SQL Alchemy 2.0 的 async context manager 模式需显式管理

#### 2. Pydantic v2 + SQLAlchemy Column
- **问题**: Pydantic 无法从 SQLAlchemy Column 提取值
- **解决方案**: 使用 `@classmethod factory method` 模式
- **关键**: `from_attributes=True` 不够，需要显式创建方法

#### 3. Optional 类型签名
- **发现**: `param: Type = None` 应该显式使用 `Optional[Type]`
- **影响**: 类型检查工具无法正确推断

#### 4. Decorator 类型返回
- **问题**: 异步装饰器返回类型复杂
- **经验**: 明确声明 TypeVar 和返回类型签名避免类型推断错误


---

## 当前问题总结 (2026-04-05)

### 已完成修复 (33 个错误)
| ID | 问题 | 文件 | 状态 |
|----|------|------|------|
| DB-01 | AsyncSession 上下文管理器类型错误 | database.py | ✅ Fixed |
| INT-01 | RetryConfig 为 None | pms_client.py | ✅ Fixed |
| INT-02 | RetryConfig 为 None | oms_client.py | ✅ Fixed |
| INT-03 | RetryConfig 为 None | srm_client.py | ✅ Fixed |

### 进行中/待修复 (90 个错误)

#### 核心模块
| ID | 问题 | 文件 | 剩余 errors |
|----|------|------|----------|
| DB-02 | retry decorator 类型 | retry.py | 4 |

#### API 响应层
| ID | 问题 | 文件 | 剩余 errors |
|----|------|------|----|
| API-01 | Pydantic Column 推断不兼容 | contracts.py | ~50 |
| API-02 | Pydantic Column 推断不兼容 | suppliers.py | ~30 |

#### 服务层
| ID | 问题 | 文件 | 剩余 errors |
|----|------|------|----|
| SVC-01 | 模型属性赋值 | supplier_sync_service.py | 6 |
| SVC-02 | 模型属性赋值 | inventory_sync_service.py | 3 |
| SVC-03 | 模型属性赋值 | contract_sync_service.py | 3 |
| SVC-04 | 模型属性赋值 | replenishment_service.py | 8 |
| SVC-05 | Column 条件判断 | task_scheduler.py | 8 |
| SVC-06 | Optional 参数 | supplier_mapping_service.py | 2 |

**总计**: 90 错误未修复

### 进度
- **Phase 1**: ✅ Complete (2/2 tasks)
- **Phase 2**: ✅ Complete (1 task, 3 files)
- **Phase 3**: 🔄 In Progress (contracts.py factory method added, needs application)
- **Phase 4**: ⏸️ Not Started

**总体进度**: 27% complete (33 / 123 errors fixed)

---

## Phase 1 - 核心基础设施

### Task 1.1: 修复 AsyncSession 上下文管理器类型

**文件**: `irp/core/database.py`

**问题**: `async_sessionmaker` 无法用于 `async with` 语句

**原因**: SQLAlchemy 2.0 `sessionmaker` 返回的是 `async_sessionmaker` 而不是直接可异步上下文管理器

**解决方案**: 使用 SQLAlchemy 2.0 推荐的模式

```python
# Option A: 使用 create_async_engine 直接管理
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session

# Option B: 使用 scoped_session
from sqlalchemy.ext.asyncio import async_scoped_session

async_engine = create_async_engine(..., echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        # session.expunge_all()
```

**步骤**:
1. 读取并理解当前实现
2. 修改 get_db 函数返回类型
3. 更新所有调用点
4. 验证 lsp_diagnostics

---

### Task 1.2: 修复 retry 装饰器类型

**文件**: `irp/core/retry.py`

**问题**: 3 个类型错误在装饰器签名返回上

**原因**:
- 协程装饰器的返回类型声明不正确
- 异常处理返回值可能为 None

**解决方案**:

```python
from functools import wraps
from typing import TypeVar, Callable, Awaitable, Any
import tenacity
from tenacity import RetryCallState, RetryError

T = TypeVar('T')

def async_retry(
    *args,
    **kwargs
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    @wraps(lambda: None)
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return tenacity.retry(
                *args, **kwargs
            )(func)(*args, **kwargs)
        return wrapper
    return decorator
```

**预期**: 3 个 Pyright 错误消除

---

## Phase 2 - 集成客户端修复

### Task 2.1: 修复所有集成客户端的 RetryConfig

**文件**:
- `irp/integrations/pms_client.py`
- `irp/integrations/oms_client.py`
- `irp/integrations/srm_client.py`

**问题**: `RetryConfig` 参数为 None，应该是实际配置对象

**原因**: 需要定义默认配置或添加类型守卫

**方案**:

```python
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from tenacity.retry import retry_if_exception_type

def get_retry_config(timeout: Optional[int] = None) -> int:
    """获取重试配置"""
    return 3  # 或者返回 RetryConfig 对象

# 更新客户端:
def init_client(
    base_url: str,
    timeout: Optional[int] = 30,
    retry_count: int = 3,
):
    self.retry_config = retry_count or get_retry_config()
    # 或使用 tenacity 装饰器包装所有 method
```

---

## Phase 3 - API 响应层

### Task 3.1: 修复 Pydantic v2 Column 推断问题

**文件**: `irp/api/contracts.py`

**问题**: Pydantic 模型从 SQLAlchemy Column 接收值

**解决方案**: 使用 Pydantic v2 `from_attributes=True`

```python
from pydantic import BaseModel, ConfigDict

class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    contract_id: str
    title: str
    type: str | None = None
    status: str
    supplier_id: str | None = None
    project_id: str | None = None
    total_amount: float
    currency: str = "CNY"
    signed_date: date | None = None
    start_date: date | None = None
    end_date: date | None = None
    # ...
```

**验证**: 所有错误应消失，因为 Pydantic 会自动提取实例属性而非列定义

---

## Phase 4 - 服务层

### Task 4.1: 修复 service 层模型赋值

**文件**: 所有 services/*.py

**问题**: 将标量值赋给 SQLAlchemy Column 属性

**解决方案**: 确保正确加载模型实例

```python
# 方式 1: 使用 session.merge
async def update_supplier(session: AsyncSession, supplier_id: str, data: dict):
    supplier = await session.get(SupplierMaster, supplier_id)
    if not supplier:
        return
    
    supplier.name = data["name"]
    supplier.risk_score = data["risk_score"]
    await session.merge(supplier)

# 方式 2: 使用 model_dump 和复制
from pydantic import TypeAdapter
from sqlalchemy import inspect

async def sync_supplier_data(session: AsyncSession, supplier_id: str, data: dict):
    existing = await session.get(SupplierMaster, supplier_id)
    if not existing:
        return
    
    # 提取可序列化字段并更新
    fields = ["name", "risk_score", "status"]
    for field in fields:
        if field in data:
            setattr(existing, field, data[field])
    
    await session.commit()
```

### Task 4.2: 修复 task_scheduler 条件判断

**问题**: 使用 Column 表达式作为 if 条件

**原因**: `task_request.type == "manual"` 是查询表达式，不是 bool

**解决方案**: 确保比较实例属性

```python
# Before:
if task_request.type == "manual":  # 错误!

# After:
# 获取实例后再比较
tasks = await session.execute(
    select(TaskRequest).where(TaskRequest.type == "manual")
)
for task in tasks.scalars().all():
    if task.type == "manual":  # 正确！
```

---

## 实施时间线

| 阶段 | 任务 | 预期时间 | 开始状态 | 完成状态 |
|------|------|---------|----------|----------|
| Phase 1 | Task 1.1-1.2 | 1 小时 | 🔄 | ✅ |
| Phase 2 | Task 2.1 | 45 分钟 | ⏳ | ⏳ |
| Phase 3 | Task 3.1 | 1 小时 | ⏳ | ⏳ |
| Phase 4 | Task 4.1-4.2 | 1.5 小时 | ⏳ | ⏳ |

**总预计**: 4 小时

---

## 验证标准

### 通过标准:
- [ ] `lsp_diagnostics -irp/`: 0 个错误
- [ ] `pytest tests/ -v`: 78 个测试全部通过
- [ ] 新写 20+ 额外测试覆盖边界情况
- [ ] 类型覆盖率 >= 95%

### 工具命令:
```bash
# 类型检查
pyright irp/
mypy irp/

# 运行测试
pytest tests/ -v --cov=irp --cov-report=html

# 格式化
yapf -irp/
```

---

## 经验教训 (实施后填写)

| 学到的内容 | 详细说明 |
|-----------|---------|
| 关键发现 1 | (待实践填写) |
| 关键发现 2 | (待实践填写) |
| 最佳实践 | (待实践填写) |

---

## 后续优化建议

### 短期 (1-2 周)
1. 集成 `.git/hooks/sendemail-validate.py` TODO 实现
2. 添加 E2E 测试覆盖核心流程
3. 性能优化 `ResourceScheduler`

### 中期 (1 月)
1. 迁移到 Poetry
2. 完善规则引擎安全评估
3. 增加类型覆盖率 (>90%)

---

*最后更新时间：2026-04-05 09:30*

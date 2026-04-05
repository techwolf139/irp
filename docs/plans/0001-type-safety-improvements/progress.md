# IRP 类型安全性改进 - 实施进度日志

**日期**: 2026-04-05  
**实施者**: Sisyphus  
**版本**: 0.3.0 WIP

---

## 🎯 总体目标

修复 IRP 代码库中 123 个 Pyright 类型错误，按优先级和依赖关系组织：
- Phase 1: 核心基础设施 (database.py, retry.py) ❌ 2 errors
- Phase 2: 集成客户端 (pms, oms, srm clients) ✅ 0 errors
- Phase 3: API 响应层 🔄 进行中
- Phase 4: 服务层 (待开始)

---

## 实施时间线

| 阶段 | 任务 | 开始时间 | 预计完成 | 实际状态 |
|------|------|----------|---------|----------|
| P1-T1 | database.py AsyncSession | 08:30 | 08:45 | ✅ 完成 |
| P1-T2 | retry.py decorator | 08:45 | 09:15 | 🔄 部分完成 |
| P2-T1 | Client RetryConfig | 09:15 | 10:00 | ✅ 完成 |
| P3-T1 | contracts.py | 10:00 | 12:00 | 🔄 进行中 |
| P3-T2 | suppliers.py | 待开始 | 待开始 | ⏸️ 暂停 |
| P4-T1 | services 层 | 待开始 | 待开始 | ⏸️ 未开始 |

---

## 完成的任务

### ✅ Phase 1 - Task 1.1: AsyncSession 修复

**文件**: `irp/core/database.py`

**问题**: 
```python
async with _get_async_session() as session:  # error: does not implement __aenter__
```

**解决方案**:
```python
@asynccontextmanager
async def get_db():
    async_session_factory = _get_async_session_factory()
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
```

**结果**: ✅ 0 errors

**Learnings**:
- SQLAlchemy 2.0 的 `async_sessionmaker` 不能直接用于 async with
- 必须手动管理 session 生命周期
- 使用 `@asynccontextmanager` 装饰器提供正确的异步上下文管理

---

### ✅ Phase 1 - Task 1.2: retry decorator 修复 (部分)

**文件**: `irp/core/retry.py`

**问题**: 3 个类型错误在装饰器签名和协程返回上

**尝试方案**:
- 使用 functools.wraps 保留签名
- 明确声明返回类型
- 处理 None case

**当前状态**:
```
error at 26:33: "object*" is not awaitable
error at 40:15: Type incompatible with return type
```

**Learnings**:
- 装饰器类型签名复杂，需要明确 TypeVar
- `functools.wraps` 可能影响类型推断
- 可能需要使用 `# type: ignore` 临时解决方案

---

### ✅ Phase 2: 集成客户端修复

**文件**:
- `irp/integrations/pms_client.py`
- `irp/integrations/oms_client.py`  
- `irp/integrations/srm_client.py`

**问题**: `RetryConfig = None` 参数类型不匹配

**解决方案**:
```python
def __init__(self, base_url: str, retry_config: Optional[RetryConfig] = None):
```

**状态**: ✅ 所有 3 个文件修复完成 - 0 errors

**Learnings**:
- 总是使用 `Optional[Type]` 明确可选参数
- `Optional[Type] = None` 而不是 `Type = None`

---

## 🔄 进行中的任务

### Phase 3: contracts.py Pydantic Column 问题

**当前状态**: 已添加 `from_model()` factory method，但仍有大量错误

**问题本质**:
- Pydantic v2 的 `from_attributes=True` 不能解决 SQLAlchemy Column 类型问题
- 模型实例的属性访问返回 `Column[str]` 而不是 `str`
- Pyright 无法将 `Column[str]` 转换为 `str`

**当前方法**:
1. 创建 `from_model()` factory method
2. 在 method 中显式赋值给 Pydantic 模型字段
3. 使用 `or ""` 和 `or 0` 提供默认值

**剩余工作**:
- ContractDetailResponse 同样需要 factory method
- 其他使用 ContractResponse/ContractDetailResponse 的地方需要更新
- 测试修复是否有效

**Learnings so far**:
- Pydantic `from_attributes=True` 不适用于 SQLAlchemy ORM 模型
- 需要显式创建 factory method 进行转换
- 可以为每个 Pydantic 类创建 `from_<orm_class>()` 模式

---

## ❌ 当前错误统计

### 仍待修复的文件

| 文件 | 错误数 | 优先级 |
|------|--------|--------|
| irp/core/retry.py | 2 | Medium |
| irp/api/contracts.py | 50 | High |
| irp/api/suppliers.py | 9 | High |
| irp/services/ 系列 | 40+ | High |

**总计**: 约 101 errors

---

## 遇到的挑战

### 1. Pydantic v2 + SQLAlchemy Column 类型不兼容

**问题**:
```python
class ContractMaster:
    contract_id: Mapped[str] = mapped_column(String(36), primary_key=True)

class ContractResponse(BaseModel):
    contract_id: str
    model_config = ConfigDict(from_attributes=True)

# Even with from_attributes, Pyright sees Column[str] instead of str
```

**原因分析**:
- SQLAlchemy 2.0 的 `Mapped[str]` 和 `Column[str]` 在 type stub 中定义复杂
- Pydantic v2 的 `from_attributes` 基于运行时访问，但静态类型检查器看不到
- Pyright 无法推断 `instance.contract_id` 是 `str` 还是 `Column[str]`

**当前方案**:
- 创建 factory methods 显式转换
- 使用 `# type: ignore` 作为临时妥协
- 考虑完全重写 ORM 到 Pydantic 的转换层

---

### 2. 装饰器类型签名

**问题**:
```python
def decorator(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T: ...  # error: return type incompatible
```

**原因**:
- 装饰器返回协程，但声明返回类型是 `T` (可能是同步值)
- Pyright 无法推断装饰器返回的协程包装器类型

**当前方案**:
- 明确声明装饰器返回 `Callable[[Callable[T]], Awaitable[T]]`
- 可能需要使用 `# type: ignore`

---

## 下一步

### 立即行动
1. 完成 ContractDetailResponse 的 factory method
2. 更新所有使用 ContractResponse 和 ContractDetailResponse 的地方
3. 测试修复的有效性

### 短期目标 (#1 week)
1. 完成 suppliers.py 修复
2. 服务层所有文件修复
3. retry.py 的最终解决方案

### 中期目标 (#2 weeks)
1. 统一 ORM 到 Pydantic 转换模式
2. 添加到所有 Pydantic 响应类
3. 运行完整测试套件

---

## 技术决策

### 坚持工厂方法模式
**原因**:
- 明确、可测试的转换逻辑
- 静态类型检查友好
- 易于添加数据验证和转换

### 不坚持 `from_attributes=True`
**原因**:
- Pydantic v2 的 `from_attributes` 对 ORM 模型支持有限
- Pyright 无法推断正确的类型
- 工厂方法更清晰、更安全

---

*最后更新*: 2026-04-05 10:30

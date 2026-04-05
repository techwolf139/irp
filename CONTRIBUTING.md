# 贡献指南

感谢您对 IRP 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 提交 Bug 报告
- 提出新功能建议
- 改进文档
- 提交代码修复
- 分享使用经验

---

## 开发环境设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd irp
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行测试

```bash
pytest tests/ -v
```

---

## 代码规范

### Python 代码风格

我们遵循 [PEP 8](https://peps.python.org/pep-0008/) 代码风格指南：

- 使用 4 个空格缩进
- 行长度限制在 88 个字符以内（Black 格式化器标准）
- 使用有意义的变量名
- 添加类型注解
- 编写文档字符串

### 类型注解

所有公共 API 必须添加类型注解：

```python
from typing import Optional, List

async def get_supplier(
    supplier_id: str,
    db: AsyncSession
) -> Optional[SupplierResponse]:
    """获取供应商详情。
    
    Args:
        supplier_id: 供应商唯一标识
        db: 数据库会话
        
    Returns:
        供应商详情，不存在则返回 None
    """
    ...
```

### 异步代码规范

- 使用 `async/await` 语法
- 数据库操作使用 SQLAlchemy 异步 API
- HTTP 请求使用 `httpx.AsyncClient`
- 避免在异步函数中使用同步阻塞操作

---

## 提交规范

我们使用 [约定式提交](https://www.conventionalcommits.org/zh-cn/v1.0.0/) 规范：

### 提交类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: add supplier risk assessment` |
| `fix` | Bug 修复 | `fix: resolve inventory calculation error` |
| `docs` | 文档更新 | `docs: update API documentation` |
| `style` | 代码格式 | `style: format with black` |
| `refactor` | 代码重构 | `refactor: optimize database queries` |
| `perf` | 性能优化 | `perf: improve sync service performance` |
| `test` | 测试相关 | `test: add unit tests for rule engine` |
| `chore` | 构建/工具 | `chore: update dependencies` |

### 提交示例

```bash
# 新增功能
git commit -m "feat: add supplier risk assessment endpoint"

# 修复 Bug
git commit -m "fix: resolve inventory calculation error when reserved_qty > sellable_qty"

# 文档更新
git commit -m "docs: add deployment guide to README"

# 破坏性变更
git commit -m "feat!: change supplier API response format

BREAKING CHANGE: supplier response now includes nested address object"
```

---

## 测试规范

### 测试覆盖率要求

- 新功能必须有单元测试覆盖
- 核心功能测试覆盖率 > 90%
- 边界条件必须测试
- 异常流程必须测试

### 测试命名规范

```python
# 测试函数命名
def test_<功能>_<场景>_<预期>():
    pass

# 示例
def test_supplier_sync_from_srm_creates_new_supplier():
    pass

def test_contract_approval_flow_purchase_four_steps():
    pass

def test_inventory_available_calculation_with_negative_result():
    pass
```

### 测试结构

```python
import pytest
from irp.services.supplier_sync_service import SupplierSyncService

class TestSupplierSyncService:
    """供应商同步服务测试。"""
    
    @pytest.fixture
    def service(self):
        return SupplierSyncService()
    
    @pytest.mark.asyncio
    async def test_sync_from_srm_creates_new_supplier(self, service, db_session):
        """测试从 SRM 同步新供应商。"""
        # Arrange
        srm_data = {...}
        
        # Act
        result = await service.sync_from_srm(db_session, srm_data)
        
        # Assert
        assert result.supplier_id == "SUP001"
        assert result.name == "测试供应商"
```

---

## Pull Request 流程

### 1. 创建分支

```bash
# 从 main 分支创建功能分支
git checkout -b feature/supplier-risk-api

# 或修复分支
git checkout -b fix/inventory-calculation
```

### 2. 开发规范

- 一个 PR 只解决一个问题
- 保持提交历史清晰
- 代码通过所有测试
- 代码通过类型检查

### 3. 提交前检查

```bash
# 运行测试
pytest tests/ -v

# 运行类型检查
mypy irp/

# 代码格式化
black irp/ tests/
isort irp/ tests/

# 代码检查
flake8 irp/ tests/
```

### 4. 提交 PR

- 填写清晰的 PR 标题和描述
- 关联相关的 Issue
- 确保 CI 检查通过
- 请求代码审查

### PR 模板

```markdown
## 描述
简要描述本次变更的目的和内容。

## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化

## 测试
- [ ] 新增测试用例
- [ ] 所有测试通过
- [ ] 手动测试验证

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 文档已更新
- [ ] 无破坏性变更（或有明确说明）
```

---

## 报告 Bug

### Bug 报告模板

提交 Bug 时，请提供以下信息：

```markdown
**问题描述**
清晰简洁地描述 Bug。

**复现步骤**
1. 执行 '...'
2. 点击 '...'
3. 看到错误

**预期行为**
描述预期应该发生什么。

**实际行为**
描述实际发生了什么。

**环境信息**
- OS: [例如 macOS 14.0]
- Python: [例如 3.12.2]
- 版本: [例如 4.0.0]

**错误日志**
```
粘贴错误日志或堆栈跟踪
```

**附加信息**
其他上下文信息或截图。
```

---

## 提出新功能

### 功能请求模板

```markdown
**功能描述**
清晰简洁地描述您想要的功能。

**使用场景**
描述这个功能将如何解决您的问题。

**预期行为**
描述您期望这个功能如何工作。

**替代方案**
描述您考虑过的替代解决方案。

**附加信息**
其他上下文信息或截图。
```

---

## 代码审查指南

### 审查重点

1. **正确性** - 代码逻辑是否正确
2. **可读性** - 代码是否易于理解
3. **性能** - 是否存在性能问题
4. **安全性** - 是否存在安全风险
5. **测试** - 测试是否充分
6. **文档** - 文档是否同步更新

### 审查反馈

- 保持友善和建设性
- 解释"为什么"而不仅是"是什么"
- 区分"必须修改"和"建议修改"
- 及时响应审查意见

---

## 发布流程

### 版本发布步骤

1. **准备发布**
   - 更新 `CHANGELOG.md`
   - 更新版本号
   - 确保所有测试通过

2. **创建发布分支**
   ```bash
   git checkout -b release/v4.1.0
   ```

3. **打标签**
   ```bash
   git tag -a v4.1.0 -m "Release version 4.1.0"
   git push origin v4.1.0
   ```

4. **创建 Release**
   - 在 GitHub 创建 Release
   - 填写发布说明
   - 附加构建产物（如有）

---

## 社区规范

### 行为准则

- 尊重所有贡献者
- 保持专业和友善
- 接受建设性批评
- 关注对社区最有利的事情

### 沟通渠道

- GitHub Issues - Bug 报告和功能请求
- GitHub Discussions - 一般性讨论
- Pull Requests - 代码审查

---

## 获得帮助

如果您在贡献过程中遇到问题：

1. 查阅相关文档
2. 搜索已有 Issues
3. 在 Discussions 中提问
4. 联系维护团队

---

感谢您的贡献！🎉

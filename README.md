# Divergent 分歧者4 IRP

<p align="center">
  <img src="https://img.shields.io/badge/version-4.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109+-009688.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/tests-78%20passed-success.svg" alt="Tests">
</p>

<p align="center">
  <b>Intelligent Resource Planning (IRP) 智能资源规划平台</b><br>
  企业级智能资源规划系统，统一管理 PMS、OMS、SRM 三大核心业务系统
</p>

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- PostgreSQL 14+
- Redis (可选，用于缓存)

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd irp

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 配置

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/irp

# 外部系统 API 地址
PMS_BASE_URL=http://pms-service:8000
OMS_BASE_URL=http://oms-service:8000
SRM_BASE_URL=http://srm-service:8000

# 应用配置
DEBUG=false
LOG_LEVEL=INFO
```

### 启动服务

```bash
# 开发模式
uvicorn irp.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn irp.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 验证安装

```bash
# 健康检查
curl http://localhost:8000/health

# 运行测试
pytest tests/ -v
```

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [📖 技术白皮书](./docs/IRP-Technical-Whitepaper.md) | 完整的系统架构和技术实现文档 |
| [📡 API 文档](./docs/API.md) | REST API 接口详细说明 |
| [🏗️ 系统设计](./docs/plans/IRP-design.md) | 系统设计方案 |
| [📋 系统总览](./docs/README.md) | PMS/OMS/SRM 三大系统功能说明 |
| [📈 更新日志](./CHANGELOG.md) | 版本更新历史 |
| [🤝 贡献指南](./CONTRIBUTING.md) | 如何参与项目贡献 |

---

## 🏛️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     IRP 智能资源规划平台                      │
├─────────────────────────────────────────────────────────────┤
│  数据聚合层                                                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                     │
│  │   PMS   │  │   OMS   │  │   SRM   │                     │
│  │ 项目管理  │  │ 订单管理  │  │ 采购管理  │                     │
│  └────┬────┘  └────┬────┘  └────┬────┘                     │
│       └─────────────┼─────────────┘                           │
│                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           IRP 统一数据层 (供应商/合同/库存/资金)          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                     │                                          │
│                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              智能服务层 (规则引擎/调度/学习)               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术选型 |
|------|----------|
| **API 框架** | FastAPI 0.109+ |
| **数据库** | PostgreSQL + SQLAlchemy 2.0 (异步) |
| **数据验证** | Pydantic v2 |
| **HTTP 客户端** | httpx (异步) |
| **测试框架** | pytest + pytest-asyncio |
| **API 文档** | OpenAPI (自动生成) |

---

## 📂 项目结构

```
irp/
├── api/                    # API 路由层
│   ├── suppliers.py        # 供应商 API
│   ├── contracts.py        # 合同 API
│   └── dashboard.py        # 看板 API
├── models/                 # 数据模型层
│   ├── supplier.py         # 供应商模型
│   ├── contract.py         # 合同模型
│   ├── inventory.py        # 库存模型
│   ├── resource.py         # 资源模型
│   └── fund.py             # 资金模型
├── services/               # 业务逻辑层
│   ├── supplier_sync_service.py
│   ├── contract_sync_service.py
│   ├── inventory_sync_service.py
│   ├── resource_scheduler.py
│   ├── rule_engine.py
│   └── ...
├── integrations/           # 外部系统集成
│   ├── pms_client.py       # PMS 集成客户端
│   ├── oms_client.py       # OMS 集成客户端
│   └── srm_client.py       # SRM 集成客户端
├── webhooks/               # Webhook 处理器
│   └── handlers.py
├── core/                   # 核心基础设施
│   ├── database.py
│   └── config.py
├── tests/                  # 测试套件
│   ├── api/
│   ├── models/
│   ├── services/
│   └── integrations/
└── main.py                 # 应用入口
```

---

## ✨ 核心功能

### 1. 供应商主数据管理
- 统一供应商信息管理
- 风险评分与等级评估
- 失信记录追踪
- 项目-供应商关联管理

### 2. 合同中心
- 树状合同结构（父合同-子合同）
- 付款计划管理
- 多类型合同审批流程
- 合同状态流转追踪

### 3. 库存视图
- 多状态库存追踪
- 实时库存聚合
- 库存预警机制
- 智能补货建议

### 4. 人力池调度
- 人+AI 混合资源池
- 智能任务分配
- 基于任务特征的分配策略

### 5. 规则引擎
- 硬约束拦截
- 软规则推荐
- 规则自动学习
- 决策一致性评估

### 6. 资金流可视化
- 多维度资金分析
- 项目级预算追踪
- 收支预测模型

---

## 🔌 API 接口

### 健康检查
```bash
GET /health
```

### 供应商 API
```bash
GET    /api/v1/suppliers              # 供应商列表
GET    /api/v1/suppliers/{id}         # 供应商详情
GET    /api/v1/suppliers/stats        # 供应商统计
```

### 合同 API
```bash
GET    /api/v1/contracts              # 合同列表
GET    /api/v1/contracts/{id}         # 合同详情
GET    /api/v1/contracts/stats        # 合同统计
POST   /api/v1/contracts/{id}/approval  # 创建审批流
```

### Webhook API
```bash
POST   /api/v1/webhook/supplier-risk-changed  # 供应商风险变更通知
```

详细 API 文档请参阅 [API.md](./docs/API.md)

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/models/ -v
pytest tests/services/ -v
pytest tests/api/ -v

# 生成覆盖率报告
pytest tests/ --cov=irp --cov-report=html
```

**当前测试状态**: 78 个测试全部通过 ✅

---

## 📝 开发指南

### 代码规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 编写单元测试覆盖新功能
- 保持异步代码的一致性

### 提交规范

```bash
# 功能开发
git commit -m "feat: add supplier risk assessment"

# Bug 修复
git commit -m "fix: resolve inventory calculation error"

# 文档更新
git commit -m "docs: update API documentation"

# 重构
git commit -m "refactor: optimize database queries"
```

---

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📈 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 4.0.0 | 2026-03-24 | 完成 Phase 1-9 全部功能 |
| 3.0.0 | 2026-03-23 | 完成 Phase 1 基础设施 |
| 2.0.0 | 2026-03-22 | 完成合同中心与库存视图 |
| 1.0.0 | 2026-03-21 | 项目初始化 |

---

## 📜 许可证

[MIT License](./LICENSE)

---

<p align="center">
  <b>Divergent 分歧者4</b> - 智能驱动，资源统一<br>
  <sub>Built with ❤️ by the IRP Team</sub>
</p>

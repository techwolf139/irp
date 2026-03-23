# Divergent 分歧者4 IRP 系统技术白皮书

> Intelligent Resource Planning (IRP) 系统
> 版本: 4.0.0
> 更新日期: 2026-03-24

---

## 目录

1. [系统概述](#1-系统概述)
2. [系统架构](#2-系统架构)
3. [核心功能模块](#3-核心功能模块)
4. [数据模型](#4-数据模型)
5. [API 接口文档](#5-api-接口文档)
6. [服务层设计](#6-服务层设计)
7. [集成方案](#7-集成方案)
8. [技术实现](#8-技术实现)
9. [部署架构](#9-部署架构)
10. [未来规划](#10-未来规划)

---

## 1. 系统概述

### 1.1 项目背景

Divergent 分歧者4 IRP (Intelligent Resource Planning) 系统是企业级智能资源规划平台，旨在统一管理来自三个核心业务系统（PMS、OMS、SRM）的数据，实现跨系统的资源可视化和智能调度。

### 1.2 系统定位

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
│                     ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           IRP 统一数据层 (供应商/合同/库存/资金)          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                     │                                            │
│                     ▼                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              智能服务层 (规则引擎/调度/学习)               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 核心能力

| 能力 | 说明 |
|------|------|
| **供应商主数据** | 统一管理来自 SRM 的供应商信息，支持风险评估和准入控制 |
| **合同中心** | 树状合同结构，支持多级子合同，完整审批流程 |
| **库存视图** | 实时库存聚合，OMS+SRM 在途联动，触发式补货 |
| **人力池** | 人力+AI 混合资源池，智能任务分配 |
| **规则引擎** | 硬约束拦截 + 软规则推荐，支持规则学习 |
| **资金流可视化** | 多维度资金分析，项目级预算追踪 |

---

## 2. 系统架构

### 2.1 技术栈

| 层级 | 技术选型 |
|------|----------|
| **API 框架** | FastAPI 0.100+ |
| **数据库** | PostgreSQL + SQLAlchemy (异步) |
| **数据验证** | Pydantic v2 |
| **HTTP 客户端** | httpx (异步) |
| **测试框架** | pytest + pytest-asyncio |
| **API 文档** | OpenAPI (自动生成) |

### 2.2 项目结构

```
irp/
├── api/                    # API 路由层
│   ├── suppliers.py        # 供应商 API
│   ├── contracts.py        # 合同 API
│   └── dashboard.py        # 看板 API
├── models/                 # 数据模型层
│   ├── supplier.py        # 供应商模型
│   ├── contract.py         # 合同模型
│   ├── inventory.py        # 库存模型
│   ├── resource.py         # 资源模型
│   └── fund.py             # 资金模型
├── services/               # 业务逻辑层
│   ├── supplier_sync_service.py
│   ├── supplier_mapping_service.py
│   ├── contract_sync_service.py
│   ├── contract_approval_service.py
│   ├── inventory_sync_service.py
│   ├── replenishment_service.py
│   ├── resource_scheduler.py
│   ├── rule_engine.py
│   ├── task_scheduler.py
│   ├── fund_sync_service.py
│   └── rule_learning_service.py
├── integrations/           # 外部系统集成
│   ├── pms_client.py       # PMS 集成客户端
│   ├── oms_client.py       # OMS 集成客户端
│   └── srm_client.py       # SRM 集成客户端
├── webhooks/               # Webhook 处理器
│   └── handlers.py
├── core/                   # 核心基础设施
│   ├── database.py
│   └── config.py
├── templates/              # 前端模板
│   └── dashboard.html
└── main.py                 # 应用入口
```

### 2.3 数据流向

```
                    ┌──────────────┐
                    │   外部系统    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   PMS    │ │   OMS    │ │   SRM    │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Sync Service │  定时同步 / Webhook
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   IRP 数据库   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Rule Engine │  规则评估
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  API Layer   │  REST API
                    └──────────────┘
```

---

## 3. 核心功能模块

### 3.1 供应商管理 (Supplier Master)

**功能描述**: 统一管理来自 SRM 的供应商主数据，支持风险评估、准入控制和项目关联。

**核心能力**:
- 供应商基础信息管理 (名称、类别、规模、注册资本)
- 风险评分与等级评估 (低/中/高)
- 失信记录追踪 (涉诉、行政处罚)
- 项目-供应商关联管理
- 供应商状态管理 (待审核/合格/不合格)

**数据同步**:
- 定时从 SRM 同步供应商数据
- Webhook 接收供应商风险变更实时通知

### 3.2 合同中心 (Contract Center)

**功能描述**: 统一管理采购合同、外包合同和框架协议，支持树状结构和审批流程。

**核心能力**:
- 合同主数据管理 (编号、标题、类型、金额、期限)
- 树状合同结构 (父合同-子合同)
- 付款计划管理 (多节点付款)
- 合同条款管理 (付款条件、交货条款、违约条款)
- 三种审批流程:
  - **采购合同**: 创建 → 采购负责人 → 法务 → 财务
  - **外包合同**: 创建 → 项目负责人 → 法务
  - **框架协议**: 创建 → 法务

**状态流转**:
```
草稿 → 生效 → 履行中 → 已完成
         ↓
       终止
```

### 3.3 库存视图 (Inventory View)

**功能描述**: 聚合 OMS 实时库存和 SRM 在途采购，监控库存健康度。

**核心能力**:
- 多状态库存追踪:
  - 可售库存 (sellable_qty)
  - 预留库存 (reserved_qty)
  - 在途库存 (in_transit_qty)
  - 质检库存 (quality_check_qty)
  - 退货库存 (returned_qty)
- 库存预警 (正常/预警/缺货/超库存)
- 自动计算可用库存 = 可售 - 预留

**补货流程**:
```
库存低于补货点 → 创建补货任务 → 多平台询价 → 生成采购申请 → 人工审批 → 正式下单
```

### 3.4 人力池 (Human Resource Pool)

**功能描述**: 统一管理人力和 AI 技能资源，支持智能任务分配。

**核心能力**:
- 人力管理:
  - 技能标签
  - 可用率 (0-1)
  - 部门/角色
  - 当前项目
- AI 资源管理:
  - 技能包
  - 能力等级
  - 调用成本
- 任务特征分析:
  - 需要判断程度
  - 需要创意程度
  - 数据密集程度
  - 可重复性

**分配策略**:
- 判断型/创意型 → 偏人力
- 数据型/重复型 → 偏 AI
- 支持混合分配

### 3.5 规则引擎 (Rule Engine)

**功能描述**: 基于规则的决策引擎，支持硬约束拦截和软规则推荐。

**核心概念**:

| 规则类型 | 说明 | 行为 |
|----------|------|------|
| HARD_CONSTRAINT | 硬约束 | BLOCK (拦截) |
| SOFT_RULE | 软规则 | PREFER/AVOID (推荐/避免) |
| LEARNED_RULE | 学习规则 | 从人工决策中提取 |

**评估流程**:
1. 硬约束检查 → 被拦截直接拒绝
2. 软规则评估 → 计算加权得分
3. 学习规则 → 基于历史决策调整
4. 综合评分 → 生成推荐/不推荐/需人工判断

**示例规则**:
```
硬约束: 失信供应商禁止合作
软规则: 合作次数>5优先, 风险评分>80降低优先级
```

### 3.6 任务调度 (Task Scheduler)

**功能描述**: 智能任务调度，支持优先级动态升级。

**优先级定义**:
- P0: 紧急
- P1: 高
- P2: 中
- P3: 低

**动态升级规则**:
| 条件 | 动作 |
|------|------|
| P2 + deadline < 2h | 升级为 P1 |
| P1 + deadline < 30min | 升级为 P0 |
| P0 + 排队 > 1h | 通知管理员 |

### 3.7 资金流可视化 (Fund Flow Visualization)

**功能描述**: 多维度资金分析，支持项目级预算追踪。

**资金类型**:
- 收入: 销售收入
- 支出: 采购支出、项目支出

**分析维度**:
- 按月份
- 按项目
- 按供应商
- 按类别

**预算视图**:
```
可用预算 = 总预算 - 已支出 - 已承诺
```

### 3.8 规则学习 (Rule Learning)

**功能描述**: 从人工决策中自动提取规则。

**学习流程**:
1. 记录人工决策 (context + decision + outcome)
2. 积累样本 (最少 5 个相似决策)
3. 检验一致性 (置信度 >= 70%)
4. 生成候选规则
5. 人工审核
6. 激活规则

---

## 4. 数据模型

### 4.1 供应商模型 (SupplierMaster)

| 字段 | 类型 | 说明 |
|------|------|------|
| supplier_id | string | 供应商唯一标识 |
| source_system | string | 来源系统 (SRM/PMS/OMS) |
| name | string | 供应商名称 |
| category | string | 供应商类别 |
| scale | string | 规模 |
| risk_score | float | 风险评分 (0-100) |
| risk_level | string | 风险等级 (Low/Medium/High) |
| is_discredited | bool | 是否失信 |
| litigation_count | int | 涉诉数量 |
| admin_penalty_count | int | 行政处罚数量 |
| rating | float | 评级 (0-5) |
| status | string | 状态 (待审核/合格/不合格) |

### 4.2 合同模型 (ContractMaster)

| 字段 | 类型 | 说明 |
|------|------|------|
| contract_id | string | 合同唯一标识 |
| type | string | 类型 (框架协议/执行合同/采购合同/外包合同) |
| status | string | 状态 (草稿/生效/履行中/已完成/终止) |
| total_amount | float | 合同金额 |
| supplier_id | string | 供应商ID |
| parent_contract_id | string | 父合同ID |
| child_contract_ids | JSON | 子合同ID列表 |

### 4.3 库存模型 (InventoryView)

| 字段 | 类型 | 说明 |
|------|------|------|
| sku_id | string | SKU唯一标识 |
| sellable_qty | int | 可售库存 |
| reserved_qty | int | 预留库存 |
| in_transit_qty | int | 在途库存 |
| available_qty | int | 可用库存 = 可售 - 预留 |
| reorder_point | int | 补货点 |
| reorder_qty | int | 补货量 |
| stock_status | string | 库存状态 |

### 4.4 资源模型 (HumanResource)

| 字段 | 类型 | 说明 |
|------|------|------|
| resource_id | string | 资源唯一标识 |
| type | string | 类型 (human/ai) |
| name | string | 资源名称 |
| skills | JSON | 技能标签列表 |
| availability | float | 可用率 (0-1) |
| status | string | 状态 (available/busy/unavailable) |
| cost_per_call | float | AI调用成本 |

### 4.5 资金模型 (FundFlow)

| 字段 | 类型 | 说明 |
|------|------|------|
| record_id | string | 记录唯一标识 |
| type | string | 类型 (收入/支出) |
| amount | float | 金额 |
| source_system | string | 来源系统 |
| category | string | 类别 |
| project_id | string | 项目ID |
| supplier_id | string | 供应商ID |
| contract_id | string | 合同ID |

---

## 5. API 接口文档

### 5.1 健康检查

**GET** `/health`

```json
Response: { "status": "healthy" }
```

### 5.2 供应商 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/suppliers` | GET | 获取供应商列表 |
| `/api/v1/suppliers/{id}` | GET | 获取供应商详情 |
| `/api/v1/suppliers/stats` | GET | 获取供应商统计 |

### 5.3 合同 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/contracts` | GET | 获取合同列表 |
| `/api/v1/contracts/{id}` | GET | 获取合同详情 |
| `/api/v1/contracts/stats` | GET | 获取合同统计 |
| `/api/v1/contracts/{id}/approval` | POST | 创建审批流 |

### 5.4 看板 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/dashboard/overview` | GET | 获取总览数据 |
| `/api/v1/dashboard/resources` | GET | 获取资源分布 |

### 5.5 Webhook API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/webhook/supplier-risk-changed` | POST | 供应商风险变更通知 |

详细 API 文档请参阅 [API.md](./API.md)

---

## 6. 服务层设计

### 6.1 同步服务架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Sync Services                            │
├─────────────────────────────────────────────────────────────┤
│  SupplierSyncService                                        │
│  ├── sync_from_srm()    定时同步 SRM 供应商数据              │
│  └── sync_from_pms()    定时同步 PMS 供应商数据              │
├─────────────────────────────────────────────────────────────┤
│  ContractSyncService                                        │
│  ├── sync_from_srm()    同步 SRM 合同                       │
│  └── link_pms_contract() 关联 PMS 子合同                     │
├─────────────────────────────────────────────────────────────┤
│  InventorySyncService                                       │
│  ├── sync_from_oms()    同步 OMS 库存                       │
│  └── sync_in_transit_from_srm() 同步在途采购               │
├─────────────────────────────────────────────────────────────┤
│  FundSyncService                                           │
│  ├── sync_from_srm()    同步 SRM 采购支出                   │
│  ├── sync_from_oms()    同步 OMS 销售收入                   │
│  └── sync_from_pms()    同步 PMS 项目预算                   │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 核心服务职责

| 服务 | 职责 |
|------|------|
| SupplierSyncService | 供应商数据同步与映射 |
| SupplierMappingService | 项目-供应商关联管理 |
| ContractSyncService | 合同数据同步与父子关联 |
| ContractApprovalService | 合同审批流程管理 |
| InventorySyncService | 库存数据聚合 |
| ReplenishmentService | 补货任务管理 |
| ResourceScheduler | 人+AI 资源分配 |
| RuleEngine | 规则评估与决策 |
| TaskScheduler | 任务调度与优先级管理 |
| FundSyncService | 资金数据同步与看板 |
| RuleLearningService | 规则自动学习 |

---

## 7. 集成方案

### 7.1 外部系统集成

**PMS (项目管理系统)**

| 接口 | 说明 |
|------|------|
| get_projects() | 获取项目列表 |
| get_persons() | 获取人员列表 |
| get_budgets() | 获取项目预算 |

**OMS (订单管理系统)**

| 接口 | 说明 |
|------|------|
| get_inventory() | 获取 SKU 库存 |
| list_inventory() | 获取库存列表 |
| get_sales() | 获取销售记录 |

**SRM (采购管理系统)**

| 接口 | 说明 |
|------|------|
| get_suppliers() | 获取供应商列表 |
| get_contracts() | 获取合同列表 |
| get_purchase_orders() | 获取采购订单 |
| get_invoices() | 获取发票 |
| create_purchase_requisition() | 创建采购申请 |
| confirm_purchase_order() | 确认采购订单 |
| get_price_comparison() | 多平台询价 |

### 7.2 数据同步策略

| 同步方式 | 适用场景 | 延迟 |
|----------|----------|------|
| 定时同步 | 批量数据同步 | 分钟级 |
| Webhook | 实时变更通知 | 秒级 |
| 手动触发 | 特殊需求 | 即时 |

---

## 8. 技术实现

### 8.1 异步架构

所有数据库操作使用 SQLAlchemy 异步驱动:

```python
from sqlalchemy.ext.asyncio import AsyncSession

async def get_suppliers(db: AsyncSession):
    result = await db.execute(select(SupplierMaster))
    return result.scalars().all()
```

### 8.2 Pydantic 数据验证

使用 Pydantic v2 进行请求/响应数据验证:

```python
class SupplierResponse(BaseModel):
    supplier_id: str
    risk_level: Optional[str]
    risk_score: float
    rating: float
    
    class Config:
        from_attributes = True
```

### 8.3 规则引擎条件评估

使用安全的表达式评估器:

```python
def evaluate_condition(self, condition: str, context: dict) -> bool:
    safe_globals = {"true": True, "false": False, "null": None}
    return eval(condition, safe_globals, context)
```

### 8.4 测试覆盖

```
tests/
├── api/
│   └── test_suppliers.py
├── models/
│   ├── test_supplier.py
│   ├── test_contract.py
│   ├── test_inventory.py
│   ├── test_resource.py
│   └── test_fund.py
├── services/
│   ├── test_supplier_sync_service.py
│   ├── test_supplier_mapping_service.py
│   ├── test_contract_sync_service.py
│   ├── test_contract_approval_service.py
│   ├── test_inventory_sync_service.py
│   ├── test_replenishment_service.py
│   ├── test_resource_scheduler.py
│   ├── test_rule_engine.py
│   ├── test_task_scheduler.py
│   ├── test_fund_sync_service.py
│   └── test_rule_learning_service.py
├── integrations/
│   ├── test_pms_client.py
│   ├── test_oms_client.py
│   └── test_srm_client.py
└── webhooks/
    └── test_handlers.py
```

**测试结果**: 78 个测试全部通过

---

## 9. 部署架构

### 9.1 环境要求

- Python 3.10+
- PostgreSQL 14+
- FastAPI 0.100+

### 9.2 环境变量配置

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/irp
SRM_BASE_URL=http://srm-service:8000
OMS_BASE_URL=http://oms-service:8000
PMS_BASE_URL=http://pms-service:8000
```

### 9.3 启动方式

```bash
# 开发环境
uvicorn irp.main:app --reload

# 生产环境
uvicorn irp.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 10. 未来规划

### 10.1 Phase 10: 高级规则引擎

- 可视化规则编辑器
- 规则版本管理
- A/B 测试框架

### 10.2 Phase 11: 高级分析

- 供应商健康度评分
- 合同履约分析
- 库存周转分析
- 资金预测模型

### 10.3 Phase 12: 移动端支持

- 移动端审批界面
- 实时库存查询
- 推送通知集成

### 10.4 Phase 13: AI 增强

- 自然语言查询
- 智能报表生成
- 异常检测与预警

---

## 附录 A: 提交记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 4.0.0 | 2026-03-24 | 完成 Phase 1-9 全部功能 |
| 3.0.0 | 2026-03-23 | 完成 Phase 1 基础设施 |
| 2.0.0 | 2026-03-22 | 完成合同中心与库存视图 |
| 1.0.0 | 2026-03-21 | 项目初始化 |

---

## 附录 B: 缩略语

| 缩写 | 全称 | 说明 |
|------|------|------|
| IRP | Intelligent Resource Planning | 智能资源规划 |
| PMS | Project Management System | 项目管理系统 |
| OMS | Order Management System | 订单管理系统 |
| SRM | Supplier Relationship Management | 供应商关系管理 |
| SKU | Stock Keeping Unit | 库存单位 |
| API | Application Programming Interface | 应用程序接口 |
| UUID | Universal Unique Identifier | 通用唯一标识符 |

---

*本文档由 Divergent 分歧者4 IRP 系统自动生成*
*最后更新: 2026-03-24*

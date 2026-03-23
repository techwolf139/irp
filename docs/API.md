# IRP API 文档

> Divergent 分歧者4 IRP 系统 API 文档

**基础路径**: `/api/v1`  
**状态**: 健康检查可用

---

## 目录

- [健康检查](#健康检查)
- [供应商 API](#供应商-api)
- [合同 API](#合同-api)
- [Webhook API](#webhook-api)
- [数据模型](#数据模型)

---

## 健康检查

### GET /health

系统健康状态检查。

**响应**:

```json
{
  "status": "healthy"
}
```

---

## 供应商 API

### 获取供应商列表

**GET** `/api/v1/suppliers`

获取所有供应商列表，支持按风险等级和状态过滤。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `risk_level` | string | 否 | 按风险等级过滤 (如 `Low`, `Medium`, `High`) |
| `status` | string | 否 | 按状态过滤 (如 `待审核`, `合格`, `不合格`) |

**响应**:

```json
[
  {
    "supplier_id": "SUP001",
    "name": "深圳市某某科技有限公司",
    "risk_level": "Low",
    "risk_score": 25.0,
    "rating": 4.5,
    "status": "合格"
  }
]
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `supplier_id` | string | 供应商唯一标识 |
| `name` | string | 供应商名称 |
| `risk_level` | string | 风险等级 (Low/Medium/High) |
| `risk_score` | float | 风险评分 (0-100) |
| `rating` | float | 供应商评级 (0-5) |
| `status` | string | 供应商状态 |

---

### 获取供应商详情

**GET** `/api/v1/suppliers/{supplier_id}`

获取指定供应商的详细信息。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `supplier_id` | string | 是 | 供应商唯一标识 |

**响应** (200 OK):

```json
{
  "supplier_id": "SUP001",
  "name": "深圳市某某科技有限公司",
  "risk_level": "Low",
  "risk_score": 25.0,
  "rating": 4.5,
  "status": "合格"
}
```

**错误响应** (404 Not Found):

```json
{
  "detail": "Supplier not found"
}
```

---

### 获取供应商统计

**GET** `/api/v1/suppliers/stats`

获取供应商统计数据。

**响应**:

```json
{
  "total": 100,
  "low_risk": 80,
  "medium_risk": 20
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | int | 供应商总数 |
| `low_risk` | int | 低风险供应商数量 |
| `medium_risk` | int | 中风险供应商数量 (总 - 低风险) |

---

## 合同 API

### 获取合同列表

**GET** `/api/v1/contracts`

获取所有合同列表，支持按状态和供应商过滤。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | string | 否 | 按状态过滤 (如 `草稿`, `生效`, `履行中`, `已完成`, `终止`) |
| `supplier_id` | string | 否 | 按供应商ID过滤 |

**响应**:

```json
[
  {
    "contract_id": "CON001",
    "title": "框架采购协议",
    "type": "框架协议",
    "status": "生效",
    "supplier_id": "SUP001",
    "project_id": null,
    "total_amount": 1000000.0,
    "currency": "CNY",
    "signed_date": "2024-01-15",
    "start_date": "2024-02-01",
    "end_date": "2024-12-31"
  }
]
```

---

### 获取合同详情

**GET** `/api/v1/contracts/{contract_id}`

获取指定合同的详细信息。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `contract_id` | string | 是 | 合同唯一标识 |

**响应** (200 OK):

```json
{
  "contract_id": "CON001",
  "title": "框架采购协议",
  "type": "框架协议",
  "status": "生效",
  "supplier_id": "SUP001",
  "project_id": null,
  "total_amount": 1000000.0,
  "currency": "CNY",
  "signed_date": "2024-01-15",
  "start_date": "2024-02-01",
  "end_date": "2024-12-31",
  "contract_no": "SRM2024001",
  "source_system": "SRM",
  "source_id": "SRM-CON001",
  "tax_rate": 0.13,
  "payment_terms": "预付30%，交付后付70%",
  "delivery_terms": "FOB Shanghai",
  "penalty_clause": "延迟交付每日千分之一",
  "child_contract_ids": ["CON001-01", "CON001-02"],
  "parent_contract_id": null
}
```

**错误响应** (404 Not Found):

```json
{
  "detail": "Contract not found"
}
```

---

### 获取合同统计

**GET** `/api/v1/contracts/stats`

获取合同统计数据。

**响应**:

```json
{
  "total": 50,
  "draft": 10,
  "active": 25,
  "completed": 10,
  "terminated": 5
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | int | 合同总数 |
| `draft` | int | 草稿状态合同数量 |
| `active` | int | 履行中合同数量 |
| `completed` | int | 已完成合同数量 |
| `terminated` | int | 终止合同数量 |

---

### 创建合同审批流

**POST** `/api/v1/contracts/{contract_id}/approval`

为合同创建审批流程。

**路径参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `contract_id` | string | 是 | 合同唯一标识 |

**请求体**:

```json
{
  "contract_type": "采购合同"
}
```

**合同类型选项**:

| 类型 | 说明 |
|------|------|
| `采购合同` | 采购审批流程 (4步) |
| `外包合同` | 外包审批流程 (3步) |
| `框架协议` | 框架协议审批流程 (2步) |

**响应**:

```json
{
  "contract_id": "CON001",
  "current_step": 0,
  "steps": [
    {"step_name": "创建", "approver_role": "采购员", "status": "pending"},
    {"step_name": "采购负责人审批", "approver_role": "采购负责人", "status": "pending"},
    {"step_name": "法务审批", "approver_role": "法务", "status": "pending"},
    {"step_name": "财务审批", "approver_role": "财务", "status": "pending"}
  ],
  "status": "pending"
}
```

**错误响应** (400 Bad Request):

```json
{
  "detail": "Invalid contract type: xxx"
}
```

---

## Webhook API

### 供应商风险变更

**POST** `/api/v1/webhook/supplier-risk-changed`

接收供应商风险变更通知。

**请求体**:

```json
{
  "supplier_id": "SUP001",
  "old_score": 25.0,
  "new_score": 75.0,
  "risk_level_changed": true,
  "new_risk_level": "High"
}
```

**请求字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `supplier_id` | string | 是 | 供应商唯一标识 |
| `old_score` | float | 是 | 变更前风险评分 |
| `new_score` | float | 是 | 变更后风险评分 |
| `risk_level_changed` | bool | 是 | 风险等级是否变更 |
| `new_risk_level` | string | 否 | 新的风险等级 |

**响应**:

```json
{
  "status": "received"
}
```

**业务逻辑**:
- 当 `risk_level_changed` 为 `true` 且 `new_risk_level` 为 `"High"` 时，触发高风险告警通知

---

## 数据模型

### SupplierMaster (供应商主数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `supplier_id` | string | 供应商唯一标识 |
| `source_system` | string | 来源系统 (PMS/OMS/SRM) |
| `source_id` | string | 源系统中的ID |
| `name` | string | 供应商名称 |
| `category` | string | 供应商类别 |
| `scale` | string | 规模 |
| `business_reg_no` | string | 工商注册号 |
| `legal_person` | string | 法人代表 |
| `registered_capital` | float | 注册资本 |
| `risk_score` | float | 风险评分 (0-100) |
| `risk_level` | string | 风险等级 |
| `is_discredited` | bool | 是否失信 |
| `litigation_count` | int | 涉诉数量 |
| `admin_penalty_count` | int | 行政处罚数量 |
| `operation_status` | string | 经营状态 |
| `rating` | float | 评级 (0-5) |
| `cooperation_count` | int | 合作次数 |
| `status` | string | 状态 (待审核/合格/不合格) |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### ProjectSupplierLink (项目供应商关联)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `project_id` | string | 项目ID |
| `supplier_id` | string | 供应商ID (外键) |
| `project_level_rating` | float | 项目级评级 |
| `project_level_tags` | JSON | 项目级标签 |
| `created_at` | datetime | 创建时间 |

### ContractMaster (合同主数据)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `contract_id` | string | 合同唯一标识 |
| `source_system` | string | 来源系统 (SRM/PMS) |
| `source_id` | string | 源系统中的ID |
| `contract_no` | string | 合同编号 |
| `title` | string | 合同标题 |
| `type` | string | 合同类型 (框架协议/执行合同/采购合同/外包合同) |
| `status` | string | 状态 (草稿/生效/履行中/已完成/终止) |
| `supplier_id` | string | 供应商ID (外键) |
| `project_id` | string | 项目ID |
| `total_amount` | float | 合同总金额 |
| `currency` | string | 币种 (默认CNY) |
| `tax_rate` | float | 税率 (默认0.13) |
| `signed_date` | date | 签订日期 |
| `start_date` | date | 开始日期 |
| `end_date` | date | 结束日期 |
| `payment_terms` | text | 付款条款 |
| `delivery_terms` | text | 交货条款 |
| `penalty_clause` | text | 违约条款 |
| `risk_flags` | JSON | 风险标志列表 |
| `child_contract_ids` | JSON | 子合同ID列表 |
| `parent_contract_id` | string | 父合同ID |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### PaymentPlan (付款计划)

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | UUID | 主键 |
| `contract_id` | string | 合同ID (外键) |
| `milestone` | string | 付款节点 |
| `amount` | float | 应付金额 |
| `due_date` | date | 应付日期 |
| `status` | string | 状态 (待付款/已付款/逾期) |
| `paid_amount` | float | 已付金额 |
| `invoice_ids` | JSON | 发票ID列表 |
| `created_at` | datetime | 创建时间 |

---

## 错误代码

| HTTP状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

*文档生成时间: 2026-03-23*

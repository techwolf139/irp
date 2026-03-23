# IRP 智能资源管理计划 - 设计文档

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建 IRP (Intelligent Resource Planning) 统一资源调度平台，打通 PMS/OMS/SRM 数据孤岛，实现"人+AI"混合资源调度与智能决策辅助。

**Architecture:** IRP 作为逻辑层位于 PMS/OMS/SRM 之上，通过变更推送+定时补偿保持数据同步。核心机制：规则引擎（硬约束）+ AI决策（软优化）+ 人工兜底 + 规则学习。

**Tech Stack:** Python API, Webhook, PostgreSQL, Redis, Kafka/RabbitMQ (可选)

---

## 一、系统定位

IRP = 资源统一调度平台 + 智能决策辅助系统

| 现有系统 | 管理的资源 | IRP中的角色 |
|----------|-----------|-------------|
| PMS | 人力、项目工时、供应商(项目级) | 人力/项目资源来源 |
| OMS | 商品、库存、订单、促销 | 库存/订单资源来源 |
| SRM | 供应商(企业级)、采购、合同、发票 | 供应商/采购资源来源 |

**IRP 运作机制**：
```
规则引擎（硬约束） → AI推荐（软优化） → 人工兜底 → 规则学习（沉淀复用）
```

---

## 二、统一资源层设计

### 2.1 供应商主数据 (优先级1)

**原则**: SRM为主，PMS依赖SRM供应商库

**数据模型**:
```yaml
SupplierMaster:
  supplier_id: str              # IRP统一标识
  source_system: str            # 来源 (SRM/PMS)
  source_id: str                # 原始ID
  
  # 基础信息
  name: str                     # 供应商名称
  category: str                 # 分类 (制造商/贸易商/服务商)
  scale: str                    # 规模 (大型/中型/小型)
  
  # SRM主数据
  business_reg_no: str          # 工商注册号
  legal_person: str             # 法人代表
  registered_capital: float     # 注册资本
  risk_score: float             # 风险评分 (0-100)
  risk_level: str               # 风险等级 (高/中/低)
  is_discredited: bool          # 失信被执行
  litigation_count: int         # 涉诉数量
  operation_status: str         # 经营状态
  
  # 关联
  contract_ids: list[str]       # 关联合同
  project_ids: list[str]        # 关联项目 (PMS)
  
  # 评估
  rating: float                 # 综合评分 (0-5)
  cooperation_count: int        # 合作次数
  
  # 状态
  status: str                   # (待审核/合格/黑名单)

ProjectSupplierLink:
  project_id: str
  supplier_id: str
  project_level_rating: float   # 项目级评分
  project_level_tags: list[str] # 项目级标签
```

**去重策略**: 人工映射表 (人工映射表明确标识同一供应商)

**IRP接口**:
```
GET  /irp/suppliers/{id}           # 获取供应商详情
GET  /irp/suppliers?risk_level=low # 查询供应商
POST /irp/supplier-link            # PMS项目关联供应商
Webhook: /irp/webhook/supplier-risk-changed  # 风险评分变更
```

---

### 2.2 合同中心 (优先级2)

**原则**: SRM合同为主，PMS合同作为子合同挂在下面

**数据模型**:
```yaml
ContractMaster:
  contract_id: str              # IRP统一合同编号
  source_system: str            # 来源 (SRM/PMS)
  source_id: str                # 原始ID
  
  # 基础
  contract_no: str              # 合同编号
  title: str                    # 标题
  type: str                     # 类型 (框架协议/执行合同/采购合同/外包合同)
  status: str                   # 状态 (草稿/生效/履行中/已完成/终止)
  
  # 关联
  supplier_id: str              # 关联供应商
  project_id: str              # 关联项目 (PMS)
  
  # 金额
  total_amount: float          # 合同总金额
  currency: str                # 币种
  tax_rate: float              # 税率
  
  # 时间
  signed_date: date            # 签订日期
  start_date: date            # 开始日期
  end_date: date              # 结束日期
  
  # 条款
  payment_terms: str           # 付款条款
  delivery_terms: str          # 交付条款
  penalty_clause: str         # 违约金条款
  risk_flags: list[str]        # 风险标记
  
  # 树状结构
  child_contract_ids: list[str] # 子合同列表 (PMS执行合同)
  parent_contract_id: str      # 父合同ID

PaymentPlan:
  contract_id: str
  milestone: str               # 付款节点
  amount: float                # 应付金额
  due_date: date               # 应付日期
  status: str                  # 状态 (待付款/已付款/逾期)
  paid_amount: float           # 已付金额
```

**合同树状结构**:
```
SRM合同 (主合同 - 框架协议)
│
├── PMS项目合同 A (执行合同 - 挂在主合同下)
│   ├── 付款节点 1: ¥10,000 (2024-06-01)
│   └── 付款节点 2: ¥15,000 (2024-09-01)
│
└── PMS项目合同 B (执行合同)
    └── 付款节点 1: ¥20,000 (2024-07-01)
```

**审批流**: 按业务类型分级
- 采购合同: 创建 → 采购负责人 → 法务 → 财务 → 生效
- 外包合同: 创建 → 项目负责人 → 法务 → 生效

**IRP接口**:
```
GET  /irp/contracts/{id}
GET  /irp/contracts?supplier_id=xxx
GET  /irp/contracts?project_id=xxx&type=child
POST /irp/contracts           # 创建合同关联
```

---

### 2.3 库存视图 (优先级3)

**原则**: OMS可售库存 + SRM采购在途 = 实际可用资源，低于阈值触发SRM采购

**数据模型**:
```yaml
InventoryView:
  sku_id: str                 # SKU编码
  sku_name: str               # SKU名称
  category: str               # 商品类目
  
  # 库存状态
  sellable_qty: int          # 可售库存 (OMS)
  reserved_qty: int           # 预留库存
  in_transit_qty: int        # 在途库存 (SRM采购)
  quality_check_qty: int      # 质检中
  returned_qty: int          # 退货在库
  
  # 计算
  available_qty: int          # 可用 = sellable - reserved
  total_qty: int             # 总库存
  
  # 补货配置
  reorder_point: int          # 补货点阈值
  reorder_qty: int           # 补货量
  lead_time_days: int        # 采购提前期
  
  # 供应商
  preferred_supplier_id: str  # 首选供应商
  backup_supplier_id: str    # 备选供应商
  
  # 状态
  stock_status: str          # (正常/预警/缺货/超库存)

ReplenishmentTask:
  task_id: str
  sku_id: str
  supplier_id: str
  qty: int
  status: str                # (待采购/采购中/已到库)
  created_at: datetime
  estimated_arrival: date
```

**触发补货流程** (半自动):
```
定时检查库存
    ↓
available_qty < reorder_point ?
    ↓ 是
创建 ReplenishmentTask (状态: 待采购)
    ↓
调用 SRM 多平台询价
    ↓
生成采购申请 (状态: 待人工确认)
    ↓
人工审批通过
    ↓
SRM 生成采购订单 (状态: 采购中)
    ↓
更新 in_transit_qty++
    ↓
到货入库 → sellable_qty++ (状态: 已到库)
```

**IRP接口**:
```
GET  /irp/inventory/{sku_id}
GET  /irp/inventory?stock_status=预警
GET  /irp/replenishment-tasks
POST /irp/replenishment-tasks/{id}/approve   # 审批采购申请
```

---

### 2.4 人力池 (优先级4)

**原则**: PMS人力 + AI技能 = 统一混合劳动力

**数据模型**:
```yaml
HumanResource:
  resource_id: str           # 统一资源ID
  type: str                 # (human/ai)
  owner: str               # 所属系统 (PMS/SRM/OMS)
  owner_id: str            # 原始ID
  
  # 人力专有
  if type == human:
    name: str              # 姓名
    skills: list[str]      # 技能标签
    availability: float    # 可用率 (0-1)
    current_projects: list[str]
    department: str
    role: str
    
  # AI专有
  if type == ai:
    name: str              # AI名称
    skill_packages: list[str] # 技能包
    capability_level: str  # (基础/高级/专业)
    api_endpoint: str     # 调用接口
    cost_per_call: float  # 单次调用成本
  
  # 调度
  preferred_task_types: list[str]
  excluded_tasks: list[str]
  status: str              # (available/busy/unavailable)

TaskRequest:
  task_id: str
  task_type: str
  
  features:
    need_judgment: float   # 需要判断 (0-1)
    need_creativity: float # 需要创意 (0-1)
    need_precision: float   # 需要精确 (0-1)
    need_execution: float  # 需要执行 (0-1)
    data_intensive: float  # 数据密集 (0-1)
    repeatability: float   # 可重复性 (0-1)
  
  constraints:
    deadline: datetime
    max_cost: float
    required_skills: list[str]
  
  preferences:
    prefer_human: bool
    prefer_ai: bool
    cost_optimization: bool
    speed_optimization: bool

ResourceAllocationPlan:
  task_id: str
  
  # 分配方案
  human_allocation:
    resource_id: str
    time_ratio: float    # 耗时占比
    tasks: list[str]     # 承担的具体任务
  
  ai_allocation:
    resource_id: str
    time_ratio: float
    tasks: list[str]
  
  # 预估
  estimated_cost: float
  estimated_time: float
  execution_order: str   # (串行/并行)
  
  # AI推荐
  ai_confidence: float  # 置信度 (0-1)
  reasoning: str        # 推荐理由
```

**AI技能管理**: 自动发现 (IRP自动扫描可用Agent服务并注册)

**调度算法**:
```
特征分析:
  - 高judgment + 高creativity → 优先人力
  - 高repeatability + 高data_intensive → 优先AI
  - 混合特征 → 人+AI分工

分配输出:
  - 方案A: 全人力
  - 方案B: 全AI
  - 方案C: 人+AI混合 (推荐)
```

**IRP接口**:
```
GET  /irp/resources                 # 人力池列表
GET  /irp/resources?type=ai&status=available
GET  /irp/resources/{id}
POST /irp/task-request             # 提交任务请求
POST /irp/task-request/{id}/allocate  # 执行分配
```

---

### 2.5 资金流向可视化 (优先级5)

**原则**: 汇总三个系统资金数据，提供统一视图

**数据模型**:
```yaml
FundFlowView:
  record_id: str
  date: date
  type: str              # (收入/支出/预算分配/转账)
  amount: float
  currency: str
  source_system: str     # (PMS/OMS/SRM)
  source_id: str        # 原始单据ID
  category: str         # 分类
  project_id: str       # 关联项目
  supplier_id: str      # 关联供应商
  contract_id: str      # 关联合同
  description: str

BudgetView:
  project_id: str
  budget_total: float   # 预算总额
  budget_spent: float  # 已支出
  budget_committed: float # 已承诺
  budget_available: float # 可用 = total - spent - committed

FundDashboard:
  total_income: float        # 总收入 (OMS)
  total_expense: float       # 总支出 (PMS+SRM)
  net_flow: float            # 净流量
  by_project: dict          # 按项目分解
  by_supplier: dict         # 按供应商分解
  by_month: dict            # 按月趋势
```

**展示维度**: 多维度仪表盘
- 时间维度: 月度趋势、收入/支出对比、净流量趋势
- 项目维度: 预算使用率、超预算预警、项目间对比
- 供应商维度: 付款排行、付款周期分析、异常大额支出
- 类型维度: 收入构成、支出构成、分类占比

**IRP接口**:
```
GET  /irp/fund-flow?group_by=month
GET  /irp/fund-flow?group_by=project
GET  /irp/budget/{project_id}
GET  /irp/dashboard
```

---

## 三、规则引擎设计

**机制**: 硬约束 (强制) + 软规则 (偏好) + 规则学习 (沉淀)

**数据模型**:
```yaml
HardConstraint:
  rule_id: str
  name: str
  description: str
  condition: Expression    # 条件表达式
  action: str             # (block/force)
  action_params: dict
  enabled: bool
  priority: int           # 冲突时按优先级

SoftRule:
  rule_id: str
  name: str
  description: str
  condition: Expression
  weight: float           # 权重 (0-1)
  direction: str          # (prefer/avoid)
  source: str             # (system/user/learned)
  confidence: float       # 置信度 (learned)
  enabled: bool

LearnedRule:
  rule_id: str
  pattern: Expression     # 从多次决策归纳
  human_decisions: list   # 原始决策
  success_metrics: dict
  confidence: float
  status: str             # (active/candidate/rejected)
```

**规则示例**:
```yaml
# 硬约束
HC001:
  name: "失信供应商禁止合作"
  condition: "supplier.is_discredited == true"
  action: "block"
  priority: 100

HC002:
  name: "超预算禁止下单"
  condition: "order.amount > budget.available"
  action: "block"
  priority: 90

# 软规则
SR001:
  name: "优先选择历史合作供应商"
  condition: "supplier.cooperation_count > 5"
  weight: 0.3
  direction: "prefer"

SR002:
  name: "避免单一供应商依赖"
  condition: "supplier.order_share > 0.5"
  weight: -0.5
  direction: "avoid"
```

**冲突处理**: 冲突时暂停，等待人工判断，记录决策作为学习样本

---

## 四、AI决策层设计

**数据模型**:
```yaml
AIRecommendation:
  recommendation_id: str
  task_type: str
  timestamp: datetime
  
  context: dict           # 上下文
  candidates: list[Candidate]
  
  ai_recommendation:
    selected_id: str
    reasoning: str
    confidence: float     # 置信度 (0-1)
    alternatives: list
  
  human_intervention:
    needed: bool
    reason: str
    final_decision: str
    decision_maker: str
    override_reason: str
  
  learning:
    outcome: str
    used_for_learning: bool

Candidate:
  candidate_id: str
  type: str              # (human/ai/both)
  resources: list
  estimated_cost: float
  estimated_time: float
  match_score: float
  constraint_satisfied: list[str]
  constraint_violated: list[str]
```

**协作模式**:
```
置信度 > 0.8 → 自动执行
置信度 0.5-0.8 → 人工确认 (简单解释)
置信度 < 0.5 → 人工决策

AI解释: 简单解释 ("推荐方案A，因为评分最高")
```

---

## 五、任务调度设计

**优先级体系**:
```yaml
TaskPriority:
  P0: { name: "紧急", sla: "<2小时", weight: 最高 }
  P1: { name: "高",   sla: "<1天",   weight: 高 }
  P2: { name: "中",   sla: "<1周",   weight: 中 }
  P3: { name: "低",   sla: "<1月",   weight: 低 }

PriorityEscalation:
  - trigger: "P2任务距deadline < 2小时 且 未开始"
    action: "升级到P1"
  - trigger: "P1任务距deadline < 30分钟 且 未开始"
    action: "升级到P0"
  - trigger: "P0任务已排队 > 1小时 且 无人接单"
    action: "提醒 + 通知主管"
```

**触发方式**:
```
被动触发 (IM/界面):
  - IM机器人 (企业微信/飞书/钉钉)
  - Web控制台
  - API接口

主动触发 (监控预警):
  - 库存水位监控 → 触发补货
  - 风险指标监控 → 发送预警
  - 截止日期监控 → 升级优先级
  - 供应商状态监控 → 风险提醒

定时触发 (周期性任务):
  - 日报生成 (每天9:00)
  - 周报评审 (每周一9:00)
  - 月度对账 (每月1日)
```

**IM交互深度**: 查询 + 轻量执行，复杂操作引导到Web

---

## 六、Web控制台设计

**角色视图**:
```
admin (管理员/运营):
  - 系统配置入口
  - 全局资源列表
  - 规则中心完整权限
  - AI决策审计
  - 用户管理

operator (业务人员):
  - 我的任务
  - 待审批队列
  - 资源搜索
  - 简单操作入口

manager (管理层):
  - 仪表盘概览
  - 资源全局视图
  - 资金流向看板
  - 报表中心
  - 风险预警汇总
```

**模块结构**:
```
IRP Web 控制台
├── 仪表盘
├── 资源管理 (供应商/合同/库存/人力/资金)
├── 任务中心 (我的任务/待审批/例外处理)
├── 规则中心 (硬约束/软规则/规则学习)
├── AI决策 (推荐历史/置信度分布)
└── 系统设置 (集成配置/AI技能/优先级/权限)
```

---

## 七、集成架构设计

**集成架构**:
```
IRP 逻辑层
    │
    ├── 读操作 (Pull) - 定时拉取各系统数据
    │   PMS: 人力/项目/工时
    │   OMS: 库存/订单
    │   SRM: 供应商/采购/合同
    │
    ├── 写操作 (Push) - 触发各系统执行
    │   PMS: 创建任务/分配资源
    │   OMS: 更新库存/处理退货
    │   SRM: 创建采购/生成合同
    │
    └── 同步机制
        - 日常: 定时拉取 (每5分钟)
        - 关键变更: 实时推送 (Webhook)
        - 失败补偿: 推送失败时下次拉取保证一致
```

**Webhook事件**:
```yaml
pms:
  - project.created/updated/deleted
  - task.created/assigned/completed
  - labor.hours_logged

oms:
  - inventory.changed
  - order.created/shipped
  - return.initiated

srm:
  - supplier.risk_changed
  - purchase_order.created/arrived
  - contract.signed
  - invoice.matched
```

---

## 八、实施优先级

**Phase 1: 基础设施**
1. IRP 基础架构搭建 (Web框架、数据库、消息队列)
2. 三大系统集成 (API + Webhook)
3. 统一资源层 - 供应商主数据

**Phase 2: 核心功能**
4. 统一资源层 - 合同中心
5. 统一资源层 - 库存视图 + 触发补货
6. 规则引擎 (硬约束 + 软规则)

**Phase 3: 智能调度**
7. 统一资源层 - 人力池 + AI技能
8. 任务调度引擎
9. AI决策层

**Phase 4: 完整闭环**
10. 统一资源层 - 资金流向可视化
11. Web控制台完善
12. 规则学习机制

---

## 九、文档索引

| 文档 | 位置 |
|------|------|
| IRP设计文档 | `docs/plans/IRP-design.md` (本文档) |
| PMS系统文档 | `docs/pms.md` |
| OMS系统文档 | `docs/oms.md` |
| SRM系统文档 | `docs/srm.md` |
| 系统总览 | `docs/README.md` |

---

*设计完成时间: 2026-03-23*

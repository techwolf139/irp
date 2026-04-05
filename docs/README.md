# IRP 系统文档总览

本文档收录 IRP 工作空间下三个核心系统的功能说明与技能清单。

<p align="center">
  <a href="./IRP-Technical-Whitepaper.md">📖 技术白皮书</a> •
  <a href="./API.md">📡 API 文档</a> •
  <a href="./plans/IRP-design.md">🏗️ 设计方案</a> •
  <a href="./plans/IRP-implementation-plan.md">📋 实施计划</a>
</p>

---

## 文档导航

| 文档 | 说明 | 适用读者 |
|------|------|----------|
| [📖 IRP-Technical-Whitepaper.md](./IRP-Technical-Whitepaper.md) | 完整的技术架构白皮书 | 架构师、技术负责人 |
| [📡 API.md](./API.md) | REST API 接口详细文档 | 前后端开发者 |
| [🏗️ plans/IRP-design.md](./plans/IRP-design.md) | 系统设计方案 | 产品经理、架构师 |
| [📋 plans/IRP-implementation-plan.md](./plans/IRP-implementation-plan.md) | 实施路线图 | 项目经理、开发者 |

---

## 系统索引

| 系统 | 目录 | 定位 |
|------|------|------|
| **PMS** | `~/git/pms/` | 项目管理系统 - 项目全生命周期管理 |
| **OMS** | `~/git/oms/` | 订单技能库 - 电商订单履约与多平台集成 |
| **SRM** | `~/git/srm/` | 采购智能体 - 企业采购全流程智能化 |

---

## PMS 项目管理系统

> 从项目全生命周期视角，覆盖进度跟踪、合同管理、供应商协作、风险监控与智能分析

### 五大核心模块

| 模块 | 能力 | 适用场景 |
|------|------|----------|
| pms-project-progress | 项目进度与任务管理 | 里程碑追踪、任务分配、进度可视化 |
| pms-contract-cost | 合同与费用管控 | 合同台账、付款计划、费用报销 |
| pms-supplier-team | 供应商与外包团队协作 | 供应商管理、团队协作、绩效评估 |
| pms-risk-quality | 风险与质量监控 | 风险识别、质量追踪、预警机制 |
| pms-analytics | 数据统计与智能分析 | 健康度评分、趋势分析、报表生成 |

### 技能清单

| 技能 | 路径 |
|------|------|
| pms-core | `skills/pms-core/` |
| pms-project-progress | `skills/pms-project-progress/` |
| pms-contract-cost | `skills/pms-contract-cost/` |
| pms-supplier-team | `skills/pms-supplier-team/` |
| pms-risk-quality | `skills/pms-risk-quality/` |
| pms-analytics | `skills/pms-analytics/` |
| pms-labor | `skills/pms-labor/` |
| pms-recruitment | `skills/pms-recruitment/` |

详细文档：[pms.md](./pms.md)

---

## OMS 订单技能库

> 从营销和产品视角，讲述如何配置业务流程解决实际问题

### 平台集成

| 平台 | 技能 |
|------|------|
| 京东开放平台 | `oms-jd-integration` |
| 小红书开放平台 | `oms-xhs-integration` |

### 核心技能

| 技能 | 用途 |
|------|------|
| oms-order-capture | 多平台订单捕获与标准化 |
| oms-one-id-merge | 用户身份归一识别 |
| oms-inventory-realtime | 实时库存查询 |
| oms-inventory-ringfence | 库存锁定防超卖 |
| oms-promotion-engine | 促销规则引擎 |
| oms-order-routing | 订单路由最优仓库 |
| oms-profit-sharing | O2O分润结算 |
| oms-returns-crosschannel | 跨渠道退货处理 |
| oms-returns-logistics | 退货物流追踪 |
| oms-reconciliation | 多平台财务对账 |

详细文档：[oms.md](./oms.md)

---

## SRM 采购智能体

> 从采购全生命周期视角，实现采购智能化

### 平台集成

| 平台 | 技能 |
|------|------|
| 国内电商（淘宝/京东/拼多多/1688） | `ecommerce-procurement-research` |
| 企业信用数据源 | `supplier-risk-assessor` |

### 核心技能

| 技能 | 用途 |
|------|------|
| srm-procurement-requirement-parser | 采购需求智能解析 |
| srm-ecommerce-procurement-research | 多平台比价询价 |
| srm-supplier-risk-assessor | 供应商准入风控 |
| srm-contract-generator | 合同模板生成 |
| srm-contract-audit | 合同AI审核 |
| srm-invoice-matcher | 三单匹配（PO/GR/Invoice） |
| srm-talent-salary-researcher | 人才薪酬对标 |
| srm-competitor-monitor | 竞品舆情监测 |
| srm-ip-infringement-scanner | 知识产权侵权巡检 |
| srm-im-bot-gateway | IM机器人集成 |
| srm-web-reader | 网页内容读取 |
| srm-asset-maintenance-tracker | 资产维保追踪 |

详细文档：[srm.md](./srm.md)

---

## 技能调用关系图

```
用户需求
    │
    ├── PMS 需求 ──────────────────────────────→ 项目管理流程
    │                                           (进度/合同/供应商/风险/分析)
    │
    ├── OMS 需求 ──────────────────────────────→ 订单履约流程
    │                                           (订单捕获/库存/促销/路由/对账)
    │
    └── SRM 需求 ──────────────────────────────→ 采购管理流程
                                                (需求解析/比价/风控/合同/三单匹配)
```

---

*文档生成时间：2026-03-23*

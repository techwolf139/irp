# PMS 项目管理系统

> 从项目全生命周期视角，覆盖进度跟踪、合同管理、供应商协作、风险监控与智能分析

**源码目录**：`~/git/pms/`

---

## 一、系统概述

PMS（Project Management System）是一套专为复杂项目场景设计的模块化管理系统，支持以下五大核心能力：

| 模块 | 能力 | 适用场景 |
|------|------|----------|
| pms-project-progress | 项目进度与任务管理 | 里程碑追踪、任务分配、进度可视化 |
| pms-contract-cost | 合同与费用管控 | 合同台账、付款计划、费用报销 |
| pms-supplier-team | 供应商与外包团队协作 | 供应商管理、团队协作、绩效评估 |
| pms-risk-quality | 风险与质量监控 | 风险识别、质量追踪、预警机制 |
| pms-analytics | 数据统计与智能分析 | 健康度评分、趋势分析、报表生成 |

---

## 二、核心业务场景

### 场景1：新项目启动与规划

**用户痛点**：项目启动时需要同时配置多个模块，人工操作繁琐且容易遗漏。

**解决思路**：
```
创建项目 → 添加里程碑 → 分配任务 → 关联供应商 → 配置风险阈值
```

### 场景2：合同履约与费用管控

**用户痛点**：合同付款节点多，容易遗漏或超付。

**解决思路**：
```
合同录入 → 设置付款节点 → 到期提醒 → 记录付款 → 费用统计
```

### 场景3：供应商绩效管理

**用户痛点**：多个供应商合作，绩效评估缺乏数据支撑。

**解决思路**：
```
供应商登记 → 协作记录 → 定期评分 → 排名分析 → 优胜劣汰
```

### 场景4：风险预警与质量管控

**用户痛点**：风险发现滞后，问题累积到后期难以收拾。

**解决思路**：
```
风险识别 → 评估等级 → 制定措施 → 持续监控 → 问题闭环
```

### 场景5：项目健康度综合分析

**用户痛点**：项目状态不透明，难以快速识别问题。

**解决思路**：
```
采集数据 → 计算维度得分 → 综合评分 → 趋势分析 → 预警推送
```

---

## 三、预置业务流程

### 流程A：项目全生命周期管理

```
项目立项 → 里程碑规划 → 任务分解 → 合同签订 → 供应商登记 → 风险识别 → 健康度分析
```

### 流程B：合同付款管理

```
合同录入 → 付款规划 → 到期提醒 → 付款记录 → 费用统计 → 报表分析
```

### 流程C：供应商协作管理

```
供应商登记 → 合同关联 → 协作记录 → 团队成员 → 绩效评分 → 供应商排名
```

---

## 四、编程接口

### Python API

```python
from pms_core import (
    SkillRunner,
    TaskManager,
    ContractManager,
    SupplierManager,
    RiskManager,
    AnalyticsManager,
    create_pms_agent
)

# 直接使用 Manager
task_mgr = TaskManager("项目A")
task = task_mgr.add_task(title="完成设计", priority="high")
progress = task_mgr.get_progress()

# 使用 SkillRunner 统一调用
runner = SkillRunner("项目A")
runner.execute("task.add", {"title": "新任务", "priority": "high"})
runner.execute("analytics.health", {})

# 使用 Agent 自然语言处理
agent = create_pms_agent("项目A")
agent.process("查看任务列表")
agent.process("添加一个高优先级的任务")
```

### 命令行接口

```bash
# 项目管理
python -m pms_core.cli project create --name "项目A"
python -m pms_core.cli project list

# 进度管理
python -m pms_core.cli progress 项目A add-task --title "完成设计"
python -m pms_core.cli progress 项目A list

# 合同管理
python -m pms_core.cli contract 项目A add --name "主合同" --amount 500000
python -m pms_core.cli contract 项目A summary

# 供应商管理
python -m pms_core.cli supplier 项目A add --name "供应商A" --category "IT服务"
python -m pms_core.cli supplier 项目A ranking

# 风险管理
python -m pms_core.cli risk 项目A add --title "人员流动风险" --severity high
python -m pms_core.cli risk 项目A dashboard

# 分析报表
python -m pms_core.cli analytics 项目A health
python -m pms_core.cli analytics 项目A report --report-type monthly

# 交互式 Shell
python -m pms_core.cli shell
```

---

## 五、数据存储结构

```
projects/
  <项目名称>/
    meta.yaml          # 项目元信息
    progress.yaml      # 任务和里程碑
    contracts.yaml     # 合同和费用
    suppliers.yaml     # 供应商和团队
    risks.yaml         # 风险和质量
    analytics.yaml     # 分析报表
```

---

## 六、典型行业方案

### 软件开发项目

**痛点**：需求变更频繁、进度难追踪、外包管理困难

**推荐流程**：
```
项目立项 → 需求里程碑 → Sprint 任务 → 外包团队协作 → 风险预警 → 质量追踪 → 月度评审
```

### 工程建设项目

**痛点**：工期紧、供应商多、风险高

**推荐流程**：
```
项目立项 → 里程碑计划 → 主合同管理 → 供应商招标 → 安全风险监控 → 质量验收 → 结算审计
```

### 咨询服务项目

**痛点**：人力成本高、客户期望管理、交付物追踪

**推荐流程**：
```
合同签订 → 阶段交付物 → 任务分配 → 工时记录 → 质量审核 → 客户满意度 → 续约分析
```

---

## 七、技能清单

| # | 技能目录 | 职能 |
|---|----------|------|
| 1 | `skills/pms-core/` | 核心引擎 |
| 2 | `skills/pms-project-progress/` | 项目进度与任务管理 |
| 3 | `skills/pms-contract-cost/` | 合同与费用管控 |
| 4 | `skills/pms-supplier-team/` | 供应商与外包团队协作 |
| 5 | `skills/pms-risk-quality/` | 风险与质量监控 |
| 6 | `skills/pms-analytics/` | 数据统计与智能分析 |
| 7 | `skills/pms-labor/` | 劳动力管理 |
| 8 | `skills/pms-recruitment/` | 招聘管理 |

---

## 八、常见问题

**Q1：如何开始使用 PMS？**
> 首先创建项目，然后根据需要启用相应模块

**Q2：支持多项目同时管理吗？**
> 支持，通过 `use <项目名>` 切换不同项目

**Q3：数据如何备份？**
> 所有数据存储在 `projects/` 目录下的 YAML 文件，可直接版本控制或备份

**Q4：可以与外部系统集成吗？**
> 通过 Python API 可集成任何外部系统

**Q5：如何生成报表？**
> 使用 `analytics` 模块的 `report` 命令，支持日/周/月/季报

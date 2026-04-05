# IRP MASFactory 集成实施计划

**日期**: 2026-04-05  
**版本**: v1.0.0  
**优先级**: High

---

## 🎯 项目目标

实现 MASFactory 框架集成，添加:
1. 图工作流编排能力支持 (Graph + Loop)
2. Vibe Graphing 自然语言到可执行图的编译
3. 人机协同交互界面
4. 可插拔的适配器系统

**预期效果**:
- ✅ 支持基于 DAG 的复杂工作流编排
- ✅ 支持循环迭代结构用于反思/重试
- ✅ 通过自然语言创建/修改工作流
- ✅ 运行时人机协同干预机制
- ✅ 代码量减少约 90%(相比手动实现)

---

## 📊 实施阶段总览

| Phase | 组件 | 文件数 | 预计时间 | 状态 |
|-------|------|:--:|--------:|:--:|
| **P1** | 基础架构 | 10 | 1.5h | ⏳ |
| **P2** | Graph 引擎 | 4 | 2h | ⏳ |
| **P3** | Vibe Graphing | 8 | 3h | ⏳ |
| **P4** | 人机协同 | 3 | 1h | ⏳ |
| **P5** | 适配器 | 6 | 1.5h | ⏳ |
| **P6** | 测试 | 4 | 2h | ⏳ |

**总计**: 35 个文件 | **8h** |

---

## 📁 文件清单

### Core Components (核心组件)
```
irp/mas_factory/core/
├── __init__.py
├── base.py              # 基础类定义
├── graph.py             # DAG Graph 实现
├── loop.py              # 循环结构实现
├── agent.py             # 智能体定义
├── node.py              # 节点基类
└── state.py             # 状态管理
```

### Components (组件库)
```
irp/mas_factory/components/
├── __init__.py
├── switch.py            # 路由开关
├── interaction.py       # 人机协同节点
├── composed_graph.py    # 复合图
└── node_template.py     # 节点模板
```

### Adapters (适配器)
```
irp/mas_factory/adapters/
├── __init__.py
├── message.py           # 消息适配器
├── context.py           # 上下文适配器
├── model.py             # 模型适配器
└── protocol.py          # 通信协议
```

### Vibe Graphing
```
irp/mas_factory/vibe/
├── __init__.py
├── graphing.py          # 主编排接口
├── role_assigner.py     # 角色分配器
├── topology_designer.py # 拓扑设计器
├── semantic_completer.py # 语义补全器
├── stages/
│   ├── stage1.py
│   ├── stage2.py
│   └── stage3.py
└── cache.py             # 设计缓存
```

### Testing
```
tests/mas_factory/
├── __init__.py
├── test_graph.py
├── test_vibe_graphing.py
├── test_adapters.py
└── fixtures.py
```

---

## 🚧 Task 1: 基础架构设置 (预计 1.5 小时)

### Task 1.1: 包结构初始化

**文件**: `irp/mas_factory/__init__.py`

```python
"""IRP MASFactory - 多智能体可视化编排框架"""

__version__ = "1.0.0"
__author__ = "IRP Team"
__all__ = [
    # Core
    "Graph",
    "Loop",
    "Agent",
    "Node",
    "State",
    
    # Components
    "Switch",
    "Interaction",
    "ComposedGraph",
    "NodeTemplate",
    
    # Vibe Graphing
    "VibeGraph",
    "VibeGraphing",
    
    # Adapters
    "MessageAdapter",
    "ContextAdapter",
]

from .core.graph import Graph
from .core.loop import Loop
from .core.agent import Agent
from .core.node import Node
from .core.state import State
from .components.switch import Switch
from .components.interaction import Interaction
from .components.composed_graph import ComposedGraph
from .components.node_template import NodeTemplate
from .vibe.graphing import VibeGraph
from .vibe.graphing import VibeGraphing
```

**文件**: `irp/mas_factory/core/__init__.py`

```python
"""MASFactory 核心组件"""

from .base import BaseComponent
from .node import Node
from .graph import Graph, Edge
from .loop import Loop
from .agent import Agent
from .state import State, WorkflowState

__all__ = [
    "BaseComponent",
    "Node",
    "Graph",
    "Edge",
    "Loop",
    "Agent",
    "State",
    "WorkflowState",
]
```

### Task 1.2: 基础类定义

**文件**: `irp/mas_factory/core/base.py`

```python
"""组件基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class BaseComponent(ABC):
    """基础组件类"""
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """验证组件有效性"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取组件信息"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "metadata": self.metadata,
        }
```

**文件**: `irp/mas_factory/core/node.py`

```python
"""节点定义"""

from typing import Any, Dict
from .base import BaseComponent

class Node(BaseComponent):
    """工作流节点基类"""
    
    async def execute(self, state: "State") -> Any:
        """执行节点逻辑"""
        raise NotImplementedError
    
    def on_enter(self, state: "State"):
        """进入节点时调用"""
        pass
    
    def on_exit(self, state: "State"):
        """退出节点时调用"""
        pass
    
    @property
    def input_fields(self) -> list[str]:
        """输入字段定义"""
        return []
    
    @property
    def output_fields(self) -> list[str]:
        """输出字段定义"""
        return []
```

**文件**: `irp/mas_factory/core/state.py`

```python
"""工作流状态管理"""

from typing import Any, Dict
from dataclasses import dataclass, field
from copy import deepcopy

@dataclass
class State:
    """工作流状态类"""
    data: Dict[str, Any] = field(default_factory=dict)
    node_history: list[str] = field(default_factory=list)
    
    def get(self, key: str) -> Any:
        """获取状态值"""
        return self.data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """设置状态值"""
        self.data[key] = value
    
    def update(self, **kwargs) -> None:
        """批量更新状态"""
        self.data.update(kwargs)
    
    def node_visited(self, node_id: str) -> None:
        """记录节点访问"""
        self.node_history.append(node_id)
    
    def copy(self) -> "State":
        """深拷贝状态"""
        return State(
            data=deepcopy(self.data),
            node_history=deepcopy(self.node_history)
        )
```

**预期**:
- ✅ 基础包结构创建成功
- ✅ 所有基类定义完整
- ✅ 导出关系正确

---

## 🚧 Task 2: Graph/DAG 引擎 (预计 2 小时)

### Task 2.1: 实现 Graph 类

**文件**: `irp/mas_factory/core/graph.py`

```python
"""DAG 有向无环图工作流实现"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from .base import BaseComponent
from .node import Node
from .state import State

@dataclass
class Edge:
    """图边定义"""
    source: str
    target: str
    metadata: Optional[Dict[str, Any]] = None
    condition: Optional[str] = None  # 可选的条件
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source": self.source,
            "target": self.target,
            "metadata": self.metadata or {},
            "condition": self.condition,
        }

class Graph(BaseComponent):
    """有向无环图工作流编排器"""
    
    def __init__(self, name: str):
        super().__init__(name=name)
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.initial_state: Dict[str, Any] = {}
        self._execution_order: List[str] = []
    
    def create_node(self, node_id: str, node: Node) -> "Graph":
        """添加节点"""
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists")
        
        if not node_id.startswith("node_"):
            node_id = f"node_{node_id}"
        
        self.nodes[node_id] = node
        self.metadata[node_id] = {
            "type": node.__class__.__name__,
            "name": node.name
        }
        return self
    
    def create_edge(self, source: str, target: str, 
                   metadata: Optional[Dict] = None,
                   condition: Optional[str] = None) -> "Graph":
        """添加边"""
        self.edges.append(Edge(
            source=f"node_{source}" if not source.startswith("node_") else source,
            target=f"node_{target}" if not target.startswith("node_") else target,
            metadata=metadata,
            condition=condition
        ))
        return self
    
    def set_initial_state(self, initial_state: Dict[str, Any]) -> "Graph":
        """设置初始状态"""
        self.initial_state = initial_state
        return self
    
    def _toposort(self) -> List[str]:
        """拓扑排序，确定执行顺序"""
        from collections import deque
        
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        # 计算入度
        for edge in self.edges:
            if edge.target in in_degree:
                in_degree[edge.target] += 1
        
        # Kahn's algorithm
        queue = deque([n for n, d in in_degree.items() if d == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for edge in self.edges:
                if edge.source == node and edge.target in in_degree:
                    in_degree[edge.target] -= 1
                    if in_degree[edge.target] == 0:
                        queue.append(edge.target)
        
        if len(result) != len(self.nodes):
            raise ValueError("Cycle detected in graph")
        
        return result
    
    def validate(self) -> bool:
        """验证图结构有效性"""
        # 验证拓扑排序
        try:
            self._toposort()
            return True
        except ValueError:
            return False
    
    async def execute(self, 
                     initial_state: Optional[Dict[str, Any]] = None,
                     debug: bool = False) -> Dict[str, Any]:
        """执行工作流"""
        # 合并状态
        state = State(data=self.initial_state)
        state.data.update(initial_state or {})
        
        # 执行拓扑排序
        order = self._toposort()
        self._execution_order = order
        
        if debug:
            print(f"Execution order: {order}")
        
        # 按序执行节点
        for node_id in order:
            node = self.nodes[node_id]
            
            # 进入前处理
            node.on_enter(state)
            
            # 执行节点
            if node_id in self._execution_order:
                result = await node.execute(state)
                state.node_visited(node_id)
            
            # 更新状态
            if isinstance(result, dict):
                state.data.update(result)
            
            # 退出后处理
            node.on_exit(state)
        
        return state.data
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "name": self.name,
            "nodes": list(self.nodes.keys()),
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        """从字典创建"""
        # 实现图的反序列化
        raise NotImplementedError
```

**预期**:
- ✅ Graph 类实现完成
- ✅ 拓扑排序正确
- ✅ 执行机制完整

---

## 🚧 Task 3: Loop 循环结构 (预计 1 小时)

**文件**: `irp/mas_factory/core/loop.py`

```python
"""循环结构支持"""

from typing import Any, Callable, Dict, Optional
from .base import BaseComponent
from .node import Node

class Loop(BaseComponent):
    """循环工作流组件
    
    用于支持迭代协作模式，如:
    - 反思
    - 修订
    - 重试
    """
    
    def __init__(self, 
                 name: str,
                 inner_graph: Any,
                 max_iterations: int = 10,
                 termination_condition: Optional[Callable] = None,
                 metadata: Optional[Dict] = None):
        """
        Args:
            name: 循环组件名称
            inner_graph: 内部图结构实例
            max_iterations: 最大迭代次数
            termination_condition: 终止条件函数
            metadata: 元数据
        """
        super().__init__(
            name=name,
            metadata={**metadata, "type": "Loop"} if metadata else {"type": "Loop"}
        )
        self.inner_graph = inner_graph
        self.max_iterations = max_iterations
        self.termination_condition = termination_condition
    
    def validate(self) -> bool:
        """验证循环定义"""
        return self.inner_graph.validate() and self.max_iterations > 0
    
    async def execute(self, state: Any, context: Optional[Dict] = None) -> Any:
        """执行循环逻辑"""
        from .state import State
        
        iteration = 0
        result = None
        
        try:
            while iteration < self.max_iterations:
                iteration += 1
                
                # 执行内部图
                state.data = result = await self.inner_graph.execute(state.data)
                
                # 检查终止条件
                if self.termination_condition and self.termination_condition(result):
                    break
                
                # 刷新状态
                if isinstance(result, dict):
                    state.data.update(result)
            else:
                raise ValueError(f"Loop exceeded max iterations ({self.max_iterations})")
            
            return result
            
        except Exception as e:
            # 异常处理
            raise e
```

**预期**:
- ✅ Loop 结构实现完成
- ✅ 迭代控制正确
- ✅ 终止条件判断准确

---

## 🚧 Task 4: Agent 智能体定义 (预计 1.5 小时)

**文件**: `irp/mas_factory/core/agent.py`

```python
"""智能体定义"""

from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel, Field
from .base import BaseComponent
from .node import Node
from .state import State

class AgentDefinition(BaseModel):
    """智能体配置定义"""
    name: str = Field(..., description="智能体名称")
    description: str = Field(..., description="智能体描述")
    skills: list[str] = Field(default_factory=list, description="技能列表")
    instructions: Optional[str] = Field(None, description="系统提示")
    tools: list[str] = Field(default_factory=list, description="可用工具")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Reviewer",
                "description": "代码审查智能体",
                "skills": ["code analysis", "security review"],
                "instructions": "你是一个专业的代码审查专家",
            }
        }

class Agent(Node):
    """工作流智能体节点
    
    基于 LLM 的智能体节点，支持:
    - 个性化提示
    - 工具使用
    - 上下文感知
    - 错误恢复
    """
    
    def __init__(self,
                 name: str,
                 agent_def: AgentDefinition,
                 model_config: Optional[Dict[str, Any]] = None,
                 context_adapters: Optional[list] = None,
                 message_adapter: Optional[str] = "json"):
        
        super().__init__(name=name)
        self.agent_def = agent_def
        self.model_config = model_config or {}
        self.context_adapters = context_adapters or []
        self.message_adapter = message_adapter
        self._llm_client = None
    
    def set_llm_client(self, client: Any) -> None:
        """设置 LLM 客户端"""
        self._llm_client = client
    
    async def execute(self, state: State) -> Dict[str, Any]:
        """执行智能体逻辑"""
        # 准备上下文
        context = await self._prepare_context(state)
        
        # 构建提示
        prompt = self._build_prompt(context)
        
        # 调用 LLM
        result = await self._call_llm(prompt, context)
        
        # 处理结果
        return self._process_result(result, context)
    
    async def _prepare_context(self, state: State) -> Dict[str, Any]:
        """准备执行上下文"""
        context = {}
        
        # 添加节点状态
        for key, value in state.data.items():
            context[key] = value
        
        # 添加历史
        context["node_history"] = state.node_history
        
        # 通过适配器处理外部上下文
        for adapter in self.context_adapters:
            adapter_data = await adapter.load_context(state)
            context.update(adapter_data)
        
        return context
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """构建执行提示"""
        message = f"""
        你是{self.agent_def.description}
        你的技能：{', '.join(self.agent_def.skills)}
        
        当前上下文:
        {context}
        
        执行任务...
        """
        return message.strip()
    
    async def _call_llm(self, prompt: str, context: Dict) -> Any:
        """调用 LLM"""
        raise NotImplementedError
    
    def _process_result(self, result: Any, context: Dict) -> Dict[str, Any]:
        """处理 LLM 返回结果"""
        # 实现结果处理逻辑
        return {"result": str(result)}
    
    @property
    def input_fields(self) -> list[str]:
        """输入字段: 上下文数据"""
        return ["context"]
    
    @property
    def output_fields(self) -> list[str]:
        """输出字段：处理结果"""
        return ["result"]
```

**预期**:
- ✅ Agent 类实现完整
- ✅ 上下文处理正确
- ✅ 执行流程清晰

---

## 📋 实施进度检查点

完成每个阶段后执行:

```bash
# 验证包导入
python -c "from irp.mas_factory import Graph, Loop, Agent; print('✅ Import OK')"

# 运行基础测试
pytest tests/mas_factory/ -v

# 验证类型安全 (可选)
pyright irp/mas_factory/ -v
```

---

## 🔗 下一步链接

- **Task 2 计划**: 详细图引擎实现
- **Task 3 计划**: Vibe Graphing 三阶段流水线
- **Task 4 计划**: 人机协同接口
- **Task 5 计划**: 适配器系统实现

---

*计划版本*: v1.0.0  
*生成时间*: 2026-04-05  
*状态*: Ready for implementation
"""Graph 有向无环图工作流实现"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import deque

from .base import BaseComponent
from .node import Node
from .state import State


@dataclass
class Edge:
    """图边定义
    
    Args:
        source: 源节点 ID
        target: 目标节点 ID
        metadata: 边元数据
        condition: 可选执行条件
    """
    source: str
    target: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "source": self.source,
            "target": self.target,
            "metadata": self.metadata or {},
            "condition": self.condition,
        }


class Graph(BaseComponent):
    """有向无环图工作流编排器
    
    支持:
    - DAG 拓扑排序
    - 并发节点执行
    - 执行状态追踪
    """
    
    def __init__(self, name: str):
        """初始化 Graph
        
        Args:
            name: 图名称
        """
        super().__init__(name=name)
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.initial_state: Dict[str, Any] = {}
        self._execution_order: List[str] = []
    
    def create_node(self, node_id: str, node: Node) -> "Graph":
        """添加节点
        
        Args:
            node_id: 节点 ID
            node: 节点实例
            
        Returns:
            self: 支持链式调用
        """
        if node_id in self.nodes:
            raise ValueError(f"Node '{node_id}' already exists")
        
        # 标准化节点 ID
        standardized_id = f"node_{node_id}" if not node_id.startswith("node_") else node_id
        
        self.nodes[standardized_id] = node
        self.metadata[standardized_id] = {
            "type": node.__class__.__name__,
            "name": node.name
        }
        return self
    
    def create_edge(self, source: str, target: str,
                   metadata: Optional[Dict] = None,
                   condition: Optional[str] = None) -> "Graph":
        """添加边
        
        Args:
            source: 源节点 ID
            target: 目标节点 ID
            metadata: 边元数据
            condition: 执行条件
            
        Returns:
            self: 支持链式调用
        """
        # 标准化节点 ID
        source_id = f"node_{source}" if not source.startswith("node_") else source
        target_id = f"node_{target}" if not target.startswith("node_") else target
        
        self.edges.append(Edge(
            source=source_id,
            target=target_id,
            metadata=metadata,
            condition=condition
        ))
        return self
    
    def set_initial_state(self, initial_state: Dict[str, Any]) -> "Graph":
        """设置初始状态
        
        Args:
            initial_state: 初始状态字典
            
        Returns:
            self: 支持链式调用
        """
        self.initial_state = initial_state
        return self
    
    def _toposort(self) -> List[str]:
        """拓扑排序，确定执行顺序
        
        Returns:
            节点 ID 列表
            
        Raises:
            ValueError: 检测到环时
        """
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
        """验证图结构有效性
        
        Returns:
            有效返回 True
        """
        if not self.nodes or not self.edges:
            return False
        
        try:
            self._toposort()
            return True
        except ValueError:
            return False
    
    async def execute(self,
                     initial_state: Optional[Dict[str, Any]] = None,
                     debug: bool = False) -> Dict[str, Any]:
        """执行工作流
        
        Args:
            initial_state: 初始状态
            debug: 是否启用调试输出
            
        Returns:
            最终状态数据
        """
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
        """转换为字典表示
        
        Returns:
            图结构字典
        """
        return {
            "name": self.name,
            "nodes": list(self.nodes.keys()),
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
        }

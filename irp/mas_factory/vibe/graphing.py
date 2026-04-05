"""Vibe Graphing 核心实现"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

from ..core.node import Node
from ..core.state import State

# Import core components
from ..core.graph import Graph
from ..core.agent import Agent, AgentDefinition


class VibeGraph(Node):
    """VibeGraph - 自然语言到可执行图的编译
    
    通过人机协同，将自然语言意图编译为可编辑的工作流规范，
    然后生成可执行的计算图。
    
    属性:
        name: Graph 名称
        build_instructions: 自然语言构建指令
        build_model: 用于构建图的模型
        invoke_model: 用于执行图的模型
        build_cache_path: 设计缓存路径
        invoke_tools: 可用的工具列表
        pull_keys: 输入数据键映射
        push_keys: 输出数据键映射
    """
    
    def __init__(self,
                 name: str,
                 build_instructions: str,
                 build_model: Any = None,
                 invoke_model: Any = None,
                 build_cache_path: Optional[str] = None,
                 invoke_tools: Optional[List[Any]] = None,
                 pull_keys: Optional[Dict[str, str]] = None,
                 push_keys: Optional[Dict[str, str]] = None):
        """初始化 VibeGraph
        
        Args:
            name: Graph 名称
            build_instructions: 构建指令 (自然语言，描述期望的工作流)
            build_model: 构建模型的实例
            invoke_model: 执行模型的实例
            build_cache_path: 设计缓存文件路径
            invoke_tools: 执行时可用工具列表
            pull_keys: 输入键映射 {code_key: field_name}
            push_keys: 输出键映射 {code_key: field_name}
        """
        super().__init__(name=name)
        
        self.build_instructions = build_instructions
        self.build_model = build_model
        self.invoke_model = invoke_model
        self.build_cache_path = build_cache_path or ""
        self.invoke_tools = invoke_tools or []
        self.pull_keys = pull_keys or {}
        self.push_keys = push_keys or {}
        
        # Compiled design
        self._graph_design: Optional[Dict[str, Any]] = None
        self._compiled_graph: Optional[Graph] = None
        
        self.metadata["type"] = "VibeGraph"
    
    def validate(self) -> bool:
        """验证 VibeGraph 配置"""
        return len(self.build_instructions) > 0
    
    def _load_or_create_design(self) -> Dict[str, Any]:
        """加载或创建图设计
        
        Returns:
            图设计字典
        """
        if self._graph_design is None:
            if Path(self.build_cache_path).exists():
                # 从缓存加载
                try:
                    with open(self.build_cache_path, 'r', encoding='utf-8') as f:
                        self._graph_design = json.load(f)
                except Exception:
                    self._graph_design = self._generate_design()
            else:
                # 生成新设计
                self._graph_design = self._generate_design()
                self._save_design()
        
        return self._graph_design
    
    def _generate_design(self) -> Dict[str, Any]:
        """生成图设计 (简化版)
        
        Returns:
            图设计字典
        """
        # 简化示例：根据构建指令生成线性工作流
        return {
            "name": self.name,
            "nodes": [
                {"id": "entry", "type": "entry", "input_fields": []},
                {"id": f"node_{self.name}_main", "type": "Agent", 
                 "input_fields": [], "output_fields": [],
                 "instructions": f"基于指令：{self.build_instructions}"}
            ],
            "edges": [
                {"source": "entry", "target": f"node_{self.name}_main"},
                {"source": f"node_{self.name}_main", "target": "exit"}
            ],
            "metadata": {
                "build_instructions": self.build_instructions,
                "build_time": "2026-04-05"
            }
        }
    
    def _save_design(self) -> None:
        """保存设计到缓存"""
        if self.build_cache_path:
            Path(self.build_cache_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.build_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self._graph_design, f, ensure_ascii=False, indent=2)
    
    async def _compile_design(self) -> None:
        """将设计编译为可执行图"""
        if self._graph_design is None:
            self._load_or_create_design()
        
        # 编译逻辑
        self._compiled_graph = Graph(name=self.name)
        
        for node_data in self._graph_design.get("nodes", []):
            node_id = node_data["id"]
            
            if node_data.get("type") in ["entry", "exit"]:
                continue
            
            # 创建节点
            if node_data.get("type") == "Agent":
                agent_def = AgentDefinition(
                    name=node_id,
                    description=node_id,
                    instructions=node_data.get("instructions", "")
                )
                node = Agent(name=node_id, agent_def=agent_def)
            else:
                # 其他节点类型
                continue
            
            # 设置输入输出字段映射
            for code_key, field_name in self.pull_keys.items():
                if code_key in node_data.get("input_fields", []):
                    node.input_fields.append(field_name)
            
            for code_key, field_name in self.push_keys.items():
                if code_key in node_data.get("output_fields", []):
                    node.output_fields.append(field_name)
            
            self._compiled_graph.create_node(node_id, node)
        
        # 添加边
        for edge_data in self._graph_design.get("edges", []):
            self._compiled_graph.create_edge(
                source=edge_data["source"],
                target=edge_data["target"]
            )
    
    async def execute(self, state: State) -> Dict[str, Any]:
        """执行 VibeGraph"""
        if self._compiled_graph is None:
            await self._compile_design()
        
        # 合并输入状态
        initial_state = {}
        for code_key, field_name in self.pull_keys.items():
            key = field_name
            if state.data.get(key):
                initial_state[code_key] = state.data.get(key)
        
        # 执行图
        result = await self._compiled_graph.execute(initial_state)
        
        # 映射输出
        output = {}
        for code_key, field_name in self.push_keys.items():
            if code_key in result:
                output[field_name] = result[code_key]
        
        return output
    
    @property
    def graph_design(self) -> Optional[Dict[str, Any]]:
        """获取图设计"""
        return self._graph_design
    
    def get_compiled_graph(self) -> Optional[Graph]:
        """获取编译后的图"""
        return self._compiled_graph


class VibeGraphing:
    """Vibe Graphing 编排器
    
    支持分阶段的人机协同：
    1. 角色分配
    2. 拓扑设计
    3. 语义补全
    
    每个阶段生成中间表示，需要用户确认才能进入下一阶段
    """
    
    def __init__(self, build_model: Any = None):
        """初始化 Vibe Graphing
        
        Args:
            build_model: 构建模型实例
        """
        self.build_model = build_model
        self.stages = ["role_assignment", "topology_design", "semantic_completion"]
        self.current_stage = 0
        self.design_progress = {}
    
    logger = logging.getLogger(__name__)
    
    async def process_request(self, user_request: str, max_iterations: int = 3) -> Dict[str, Any]:
        """处理用户请求，生成最终图设计
        
        Args:
            user_request: 用户的自然语言请求
            max_iterations: 最大迭代次数
            
        Returns:
            最终图设计字典
        """
        self.design_progress = {}
        
        for stage in self.stages:
            if stage == "role_assignment":
                result = await self._role_assignment_stage(user_request)
            elif stage == "topology_design":
                result = await self._topology_design_stage(user_request)
            elif stage == "semantic_completion":
                result = await self._semantic_completion_stage(user_request)
            
            self.design_progress[stage] = result
            
            # 检查是否完成
            if stage == "semantic_completion":
                break
        
        return self.design_progress
    
    async def _role_assignment_stage(self, user_request: str) -> Dict[str, Any]:
        """角色分配阶段
        
        Returns:
            角色分配结果
        """
        # 调用模型生成角色分配
        return {"role_mapping": "Generated based on request"}
    
    async def _topology_design_stage(self, user_request: str) -> Dict[str, Any]:
        """拓扑设计阶段
        
        Returns:
            拓扑设计结果
        """
        return {"graph_structure": "Generated based on role mapping"}
    
    async def _semantic_completion_stage(self, user_request: str) -> Dict[str, Any]:
        """语义补全阶段
        
        Returns:
            最终图设计
        """
        # 生成完整设计
        return {
            "nodes": [
                {"id": f"node_{self.name}", "type": "Agent", 
                 "instructions": f"基于：{user_request}",
                 "input_fields": [], "output_fields": []}
            ],
            "edges": [
                {"source": "ENTRY", "target": f"node_{self.name}"},
                {"source": f"node_{self.name}", "target": "EXIT"}
            ]
        }

"""VibeGraph 核心实现 - 三阶段流水线集成

集成 RoleAssigner, TopologyDesigner, SemanticCompleter 和缓存机制
"""

from typing import Any, Dict, List, Optional
from ..core.node import Node
from .stage_components import (
    RoleAssigner,
    TopologyDesigner,
    SemanticCompleter,
    VibeGraphStages
)
from .cache import DesignCache, GraphDesignMetadata


class VibeGraphAdvanced(Node):
    """增强版 VibeGraph - 完整三阶段实现
    
    支持：
    - 三阶段流水线 (角色→拓扑→语义)
    - JSON 缓存管理
    - 设计元数据追踪
    """
    
    def __init__(self,
                 name: str,
                 build_instructions: str,
                 build_model: Any = None,
                 invoke_model: Any = None,
                 cache_path: str = "./cache/vibe_graphs"):
        """初始化 VibeGraph
        
        Args:
            name: Graph 名称
            build_instructions: 构建指令
            build_model: 构建模型
            invoke_model: 执行模型
            cache_path: 缓存路径
        """
        super().__init__(name=name)
        
        self.build_instructions = build_instructions
        self.build_model = build_model
        self.invoke_model = invoke_model
        self.cache = DesignCache(cache_path)
        
        # 实现阶段组件
        self.stages = VibeGraphStages(build_model)
        
        # 缓存状态
        self._latest_design: Optional[Dict[str, Any]] = None
        self._metadata: Optional[GraphDesignMetadata] = None
    
    def validate(self) -> bool:
        """验证 VibeGraph 配置"""
        return len(self.build_instructions) > 0
    
    async def _generate_design(self) -> Dict[str, Any]:
        """执行三阶段生成
        
        Returns:
            图设计字典
        """
        # 阶段 1: 角色分配
        roles = await self.stages.role_assigner.assign_roles(self.build_instructions)
        
        # 阶段 2: 拓扑设计
        topology = self.stages.topology_designer.design_topology(roles)
        
        # 阶段 3: 语义补全
        final_config = self.stages.semantic_completer.complete_semantics(
            topology=topology,
            roles=roles,
            user_intent=self.build_instructions
        )
        
        # 更新元数据
        self._metadata = GraphDesignMetadata(
            user_intent=self.build_instructions,
            role_count=len(roles),
            node_count=len(final_config.get("nodes", []))
        )
        
        return final_config
    
    async def _load_design(self) -> bool:
        """尝试加载缓存设计
        
        Returns:
            成功加载返回 True
        """
        # 简化版：直接生成新设计
        design = await self._generate_design()
        self._latest_design = design
        
        # 保存到缓存
        cache_path = self.cache.get_cache_path(design)
        if self.cache.save(design, cache_path):
            print(f"✓ Design cached to: {cache_path}")
        
        return True
    
    async def execute(self, state: "State") -> Dict[str, Any]:
        """执行 VibeGraph"""
        if self._latest_design is None:
            await self._load_design()
        
        # 返回设计结果
        return {
            "design": self._latest_design,
            "metadata": self._metadata.to_dict() if self._metadata else {}
        }
    
    def get_latest_design(self) -> Optional[Dict[str, Any]]:
        """获取最新设计"""
        return self._latest_design
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """获取元数据"""
        return self._metadata.to_dict() if self._metadata else None

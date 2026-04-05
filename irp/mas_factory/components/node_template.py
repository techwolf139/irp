"""节点模板定义"""

from typing import Any, Dict, List, Optional, Type

from ..core.base import BaseComponent


class NodeTemplate:
    """节点模板
    
    允许先声明结构模板，然后实例化为具体图
    支持：
    - 声明与实例化解耦
    - 克隆模板构建多个图
    - 版本化管理
    """
    
    def __init__(self,
                 graph_type: type,
                 invoke_model: Any = None,
                 build_model: Any = None,
                 build_instructions: str = "",
                 build_cache_path: str = ""):
        """初始化节点模板
        
        Args:
            graph_type: 图类型 (如 VibeGraph)
            invoke_model: 执行模型
            build_model: 构建模型
            build_instructions: 构建指令 (自然语言)
            build_cache_path: 缓存路径
        """
        self.graph_type = graph_type
        self.invoke_model = invoke_model
        self.build_model = build_model
        self.build_instructions = build_instructions
        self.build_cache_path = build_cache_path
    
    def clone(self, name: str = None, **overrides) -> "NodeTemplate":
        """克隆模板
        
        Args:
            name: 新名称
            **overrides: 覆盖参数
            
        Returns:
            克隆的模板实例
        """
        return NodeTemplate(
            graph_type=self.graph_type,
            invoke_model=overrides.get("invoke_model", self.invoke_model),
            build_model=overrides.get("build_model", self.build_model),
            build_instructions=overrides.get("build_instructions", self.build_instructions),
            build_cache_path=overrides.get("build_cache_path", self.build_cache_path)
        )

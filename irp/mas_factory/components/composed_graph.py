"""模板化原型设计组件"""

from typing import Any, Dict, List, Optional
from copy import deepcopy

from ..core.base import BaseComponent


class ComposedGraph(BaseComponent):
    """复合图组件
    
    用于表示一类预定义的结构，支持：
    - 可复用模板
    - 参数化实例化
    - 隐藏底层构建细节
    """
    
    def __init__(self,
                 name: str,
                 template: "ComposedGraph",
                 description: str = "",
                 parameters: List[Dict[str, Any]] = None):
        """初始化 ComposedGraph
        
        Args:
            name: 组件名称
            template: 底层模板实例
            description: 描述
            parameters: 参数定义列表
        """
        super().__init__(
            name=name,
            metadata={
                "type": "ComposedGraph",
                "description": description,
                "parameters": parameters or []
            }
        )
        self.template = template
        self.parameters = parameters or []
    
    def validate(self) -> bool:
        """验证复合图定义"""
        return self.template is not None and self.template.validate()
    
    def clone(self, **overrides) -> "ComposedGraph":
        """克隆复合图并修改参数
        
        Returns:
            新的 ComposedGraph 实例
        """
        cloned = ComposedGraph(
            name=overrides.get("name", self.name),
            template=deepcopy(self.template),
            description=self.description,
            parameters=self.parameters
        )
        # 应用覆盖参数
        for key, value in overrides.items():
            if key != "name":
                setattr(cloned, key, value)
        return cloned
    
    async def execute(self, state: Any, context: Optional[Dict] = None) -> Any:
        """执行复合图
        
        Returns:
            执行结果
        """
        # 调用底层模板执行
        return await self.template.execute(state)


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

"""路由开关组件"""

from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel
from ..core.base import BaseComponent


class Switch(BaseComponent):
    """路由开关组件
    
    在图中实现动态路径选择，根据运行时状态激活不同子图
    """
    
    def __init__(self,
                 name: str,
                 routing_rule: Callable[[Dict[str, Any]], str],
                 paths: List[str],
                 default_path: str):
        """初始化 Switch
        
        Args:
            name: 组件名称
            routing_rule: 路由规则函数 (state -> path_name)
            paths: 可选路径列表
            default_path: 默认路径
        """
        super().__init__(name=name)
        self.routing_rule = routing_rule
        self.paths = paths
        self.default_path = default_path
        self.metadata["type"] = "Switch"
    
    def validate(self) -> bool:
        """验证 Switch 定义"""
        return len(self.paths) > 0 and self.default_path in self.paths
    
    def route(self, state: Dict[str, Any]) -> str:
        """根据状态路由
        
        Returns:
            选定的路径名称
        """
        try:
            path = self.routing_rule(state)
            if path in self.paths:
                return path
        except Exception:
            # 路由规则失败时返回默认路径
            pass
        return self.default_path

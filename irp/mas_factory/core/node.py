"""工作流节点定义"""

from typing import Any, Dict, Optional
from .base import BaseComponent
from .state import State


class Node(BaseComponent):
    """节点基类
    
    工作流中的基本计算单元，支持执行生命周期钩子
    """
    
    async def execute(self, state: "State") -> Any:
        """执行节点逻辑
        
        Args:
            state: 当前工作流状态
            
        Returns:
            执行结果，可以是任意类型
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def on_enter(self, state: "State"):
        """进入节点时调用
        
        Args:
            state: 当前工作流状态
        """
        pass
    
    def on_exit(self, state: "State"):
        """退出节点时调用
        
        Args:
            state: 当前工作流状态
        """
        pass
    
    @property
    def input_fields(self) -> list[str]:
        """输入字段定义"""
        return []
    
    @property
    def output_fields(self) -> list[str]:
        """输出字段定义"""
        return []

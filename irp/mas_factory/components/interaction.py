"""人机协同节点"""

from typing import Any, Dict, List, Optional

from ..core.base import BaseComponent
from ..core.state import State


class Interaction(BaseComponent):
    """人机协同节点
    
    在运行时收集用户输入，支持交互式干预
    """
    
    def __init__(self,
                 name: str,
                 human_instructions: str,
                 options: List[str] = None,
                 input_fields: List[str] = None,
                 cache_path: Optional[str] = None):
        """初始化 Interaction 节点
        
        Args:
            name: 节点名称
            human_instructions: 人机交互提示
            options: 快捷选项列表 (可选)
            input_fields: 需要用户输入的数据字段
            cache_path: 缓存文件路径
        """
        super().__init__(name=name)
        self.human_instructions = human_instructions
        self.options = options or []
        self.input_fields = input_fields or []
        self.cache_path = cache_path
        self.metadata["type"] = "Interaction"
    
    def validate(self) -> bool:
        """验证 Interaction 定义"""
        return len(self.human_instructions) > 0
    
    async def interact(self, state: State) -> Dict[str, Any]:
        """与用户交互
        
        Returns:
            用户输入结果字典
        """
        # 简化版：提示用户输入
        print(f"\n[INTERACTION] {self.human_instructions}")
        
        if self.options:
            print(f"选项：{self.options}")
            result = input("请选择 (输入选项或 'custom' 自定义): ")
            if result in self.options:
                return {"user_selection": result}
            else:
                return {"user_selection": result, "custom_input": True}
        else:
            user_input = input("请输入：")
            return {"user_input": user_input}
    
    async def execute(self, state: State) -> Dict[str, Any]:
        """执行交互节点"""
        return await self.interact(state)

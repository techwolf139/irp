"""循环结构支持"""

from typing import Any, Callable, Dict, Optional

from .base import BaseComponent
from .graph import Graph


class Loop(BaseComponent):
    """循环工作流组件
    
    用于支持迭代协作模式，如：
    - 反思
    - 修订
    - 重试
    """
    
    def __init__(self,
                 name: str,
                 inner_graph: Graph,
                 max_iterations: int = 10,
                 termination_condition: Optional[Callable] = None,
                 metadata: Optional[Dict] = None):
        """初始化 Loop
        
        Args:
            name: 循环组件名称
            inner_graph: 内部图结构实例
            max_iterations: 最大迭代次数
            termination_condition: 终止条件函数 (result -> bool)
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
        """验证循环定义
        
        Returns:
            有效返回 True
        """
        return self.inner_graph.validate() and self.max_iterations > 0
    
    async def execute(self,
                     state: Any,
                     context: Optional[Dict] = None) -> Any:
        """执行循环逻辑
        
        Args:
            state: 当前状态
            context: 上下文信息
            
        Returns:
            执行结果
            
        Raises:
            ValueError: 超出最大迭代次数时
        """
        from .state import State
        
        iteration = 0
        result = None
        
        try:
            while iteration < self.max_iterations:
                iteration += 1
                
                # 执行内部图
                if isinstance(state, State):
                    state.data = result = await self.inner_graph.execute(state.data)
                else:
                    result = await self.inner_graph.execute(state)
                
                # 检查终止条件
                if self.termination_condition and self.termination_condition(result):
                    break
            
            return result
            
        except Exception as e:
            if iteration >= self.max_iterations:
                raise ValueError(f"Loop exceeded max iterations ({self.max_iterations})")
            raise e

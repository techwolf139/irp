"""状态管理模块"""

from typing import Any, Dict
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class State:
    """工作流状态类
    
    用于在节点间传递数据，支持读写、拷贝和访问历史
    """
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

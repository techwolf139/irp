"""组件基类定义"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class BaseComponent(ABC):
    """基础组件类
    
    所有 MASFactory 组件的基类，提供统一的元数据和验证接口
    """
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """验证组件有效性"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """获取组件信息"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "metadata": self.metadata,
        }

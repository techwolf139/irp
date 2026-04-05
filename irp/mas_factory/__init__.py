"""IRP MASFactory - 多智能体可视化编排框架

基于 MASFactory 的图工作流编排能力，支持 VibeGraph自然语言到可执行图编译
实现人机协同交互、可插拔适配器系统

版本: 1.0.0
作者: IRP Team
"""

__version__ = "1.0.0"
__author__ = "IRP Team"

# Core exports
from .core.graph import Graph, Edge
from .core.loop import Loop
from .core.agent import Agent, AgentDefinition
from .core.node import Node
from .core.state import State

# Components exports
from .components.switch import Switch
from .components.interaction import Interaction
from .components.composed_graph import ComposedGraph
from .components.node_template import NodeTemplate

# Vibe Graphing exports
from .vibe.graphing import VibeGraph
from .vibe.graphing import VibeGraphing

# Adapters exports
from .adapters.message import MessageAdapter
from .adapters.context import ContextAdapter
from .adapters.model import ModelAdapter

__all__ = [
    # Core
    "Graph",
    "Edge",
    "Loop",
    "Agent",
    "AgentDefinition",
    "Node",
    "State",
    
    # Components
    "Switch",
    "Interaction",
    "ComposedGraph",
    "NodeTemplate",
    
    # Vibe Graphing
    "VibeGraph",
    "VibeGraphing",
    
    # Adapters
    "MessageAdapter",
    "ContextAdapter",
    "ModelAdapter",
]

"""上下文适配器"""

from typing import Any, Dict, List, Optional
from ..core.base import BaseComponent


class ContextAdapter(BaseComponent):
    """上下文适配器
    
    将不同信息源 (Memory, MCP, RAG) 的异构性屏蔽，提供统一接口
    所有适配器最终产生 ContextBlock 单元
    """
    
    def __init__(self, name: str, context_label: str):
        """初始化上下文适配器
        
        Args:
            name: 适配器名称
            context_label: 上下文标签
        """
        super().__init__(name=name)
        self.context_label = context_label
        self.metadata["type"] = "ContextAdapter"
    
    async def load_context(self, state: Any) -> Dict[str, Any]:
        """加载上下文数据
        
        Raises:
            NotImplementedError: 子类需要实现
        """
        raise NotImplementedError("Subclasses must implement load_context()")


class ContextBlock:
    """上下文数据块
    
    属性:
        text: 文本内容
        score: 相关度分数
        uri: 来源 URI
        context_label: 上下文标签
    """
    
    def __init__(self, text: str, score: float = 0.0, uri: str = "", context_label: str = ""):
        """初始化上下文块
        
        Args:
            text: 文本内容
            score: 相关度分数
            uri: 来源 URI
            context_label: 上下文标签
        """
        self.text = text
        self.score = score
        self.uri = uri
        self.context_label = context_label
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "text": self.text,
            "score": self.score,
            "uri": self.uri,
            "context_label": self.context_label
        }


class MCPAdapter(ContextAdapter):
    """MCP (Model Context Protocol) 适配器
    
    用于集成外部数据源，如企业知识库、搜索引擎等
    """
    
    def __init__(self,
                 name: str,
                 call_func: Any,
                 passive: bool = False,
                 active: bool = False):
        """初始化 MCP 适配器
        
        Args:
            name: 适配器名称
            call_func: MCP 调用函数
            passive: 被动模式
            active: 主动模式
        """
        super().__init__(name=name, context_label="MCP")
        self.call_func = call_func
        self.passive = passive
        self.active = active
    
    async def load_context(self, state: Any) -> Dict[str, Any]:
        """从 MCP 加载上下文"""
        # 调用外部 MCP 服务
        if hasattr(self, 'query_text'):
            results = await self.call_func(self.query_text)
            return results
        return {}


class RAGAdapter(ContextAdapter):
    """RAG (检索增强生成) 适配器
    
    用于集成向量数据库或搜索引擎
    """
    
    def __init__(self, name: str, vector_db: Any, query_field: str = "query"):
        """初始化 RAG 适配器
        
        Args:
            name: 适配器名称
            vector_db: 向量数据库客户端
            query_field: 查询字段名
        """
        super().__init__(name=name, context_label="RAG")
        self.vector_db = vector_db
        self.query_field = query_field
    
    async def load_context(self, state: Any) -> Dict[str, Any]:
        """从向量数据库检索上下文"""
        # 简化版实现
        query = state.get(self.query_field, "")
        if not query:
            return {}
        
        # 调用检索
        results = await self.vector_db.search(query, top_k=5)
        blocks = [
            ContextBlock(text=r["text"], score=r["score"])
            for r in results
        ]
        return {
            "rag_context": [b.to_dict() for b in blocks]
        }

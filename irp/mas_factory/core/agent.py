"""智能体定义"""

from typing import Any, Callable, Dict, Optional

from pydantic import BaseModel, Field
from .base import BaseComponent
from .node import Node
from .state import State


class AgentDefinition(BaseModel):
    """智能体配置定义
    
    属性:
        name: 智能体名称
        description: 智能体描述
        skills: 技能列表
        instructions: 系统提示
        tools: 可用工具
    """
    name: str = Field(..., description="智能体名称")
    description: str = Field(..., description="智能体描述")
    skills: list[str] = Field(default_factory=list, description="技能列表")
    instructions: Optional[str] = Field(None, description="系统提示")
    tools: list[str] = Field(default_factory=list, description="可用工具")


class Agent(Node):
    """工作流智能体节点
    
    基于 LLM 的智能体节点，支持：
    - 个性化提示
    - 工具使用
    - 上下文感知
    - 错误恢复
    """
    
    def __init__(self,
                 name: str,
                 agent_def: AgentDefinition,
                 model_config: Optional[Dict[str, Any]] = None,
                 context_adapters: Optional[list] = None,
                 message_adapter: Optional[str] = "json"):
        """初始化 Agent
        
        Args:
            name: 智能体名称
            agent_def: 智能体定义
            model_config: 模型配置
            context_adapters: 上下文适配器列表
            message_adapter: 消息适配器类型
        """
        super().__init__(name=name)
        self.agent_def = agent_def
        self.model_config = model_config or {}
        self.context_adapters = context_adapters or []
        self.message_adapter = message_adapter
        self._llm_client = None
    
    def set_llm_client(self, client: Any) -> None:
        """设置 LLM 客户端"""
        self._llm_client = client
    
    async def execute(self, state: State) -> Dict[str, Any]:
        """执行智能体逻辑
        
        Returns:
            执行结果字典
        """
        # 准备上下文
        context = await self._prepare_context(state)
        
        # 构建提示
        prompt = self._build_prompt(context)
        
        # 调用 LLM
        result = await self._call_llm(prompt, context)
        
        # 处理结果
        return self._process_result(result, context)
    
    async def _prepare_context(self, state: State) -> Dict[str, Any]:
        """准备执行上下文
        
        Returns:
            上下文字典
        """
        context = {}
        
        # 添加节点状态
        for key, value in state.data.items():
            context[key] = value
        
        # 添加历史
        context["node_history"] = state.node_history
        
        # 通过适配器处理外部上下文
        for adapter in self.context_adapters:
            adapter_data = await adapter.load_context(state)
            context.update(adapter_data)
        
        return context
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """构建执行提示
        
        Returns:
            提示字符串
        """
        message = f"""
        你是{self.agent_def.description}
        你的技能：{', '.join(self.agent_def.skills)}
        
        当前上下文:
        {context}
        
        执行任务...
        """
        return message.strip()
    
    async def _call_llm(self, prompt: str, context: Dict) -> Any:
        """调用 LLM
        
        Returns:
            模拟的 LLM 响应
        """
        # 简化版：返回模拟响应用于测试
        return {
            "response": f"Processed: {prompt[:50]}...",
            "context_used": list(context.keys())
        }
    
    def _process_result(self, result: Any, context: Dict) -> Dict[str, Any]:
        """处理 LLM 返回结果
        
        Returns:
            处理后的结果字典
        """
        # 简化版处理
        return {"result": str(result)}
    
    @property
    def input_fields(self) -> list[str]:
        """输入字段：上下文数据"""
        return ["context"]
    
    @property
    def output_fields(self) -> list[str]:
        """输出字段：处理结果"""
        return ["result"]
    
    def validate(self) -> bool:
        """验证 Agent 定义"""
        if not self.agent_def.name or not self.agent_def.description:
            return False
        
        return bool(
            self.agent_def.name
            and self.agent_def.description
        )

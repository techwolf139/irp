"""模型适配器定义"""

from typing import Any, Dict, Optional

from ..core.base import BaseComponent


class ModelAdapter(BaseComponent):
    """模型适配器
    
    用于封装 LLM 客户端接口，支持：
    - OpenAI
    - 其他兼容 OpenAPI 格式的模型
    - 自定义模型客户端
    """
    
    def __init__(self, name: str, client: Any, model_name: str = "gpt-4o-mini"):
        """初始化模型适配器
        
        Args:
            name: 适配器名称
            client: LLM 客户端
            model_name: 模型名称
        """
        super().__init__(name=name)
        self.client = client
        self.model_name = model_name
        self.metadata["type"] = "ModelAdapter"
    
    async def generate(self, prompt: str) -> str:
        """生成文本回复
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        raise NotImplementedError("Subclasses must implement generate()")


class OpenAIModelAdapter(ModelAdapter):
    """OpenAI 模型适配器扩展定义"""
    
    def __init__(self,
                 api_key: str,
                 base_url: str = "",
                 model_name: str = "gpt-4o-mini"):
        """初始化 OpenAI 模型适配器
        
        Args:
            api_key: API 密钥
            base_url: API 基础 URL
            model_name: 模型名称
        """
        super().__init__(
            name="openai_adapter",
            client=None,  # 延迟加载
            model_name=model_name
        )
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
    
    def validate(self) -> bool:
        """验证适配器配置"""
        return len(self.api_key) > 0

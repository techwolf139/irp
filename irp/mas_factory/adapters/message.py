"""消息适配器"""

from typing import Any, Dict, Optional
from ..core.base import BaseComponent


class MessageAdapter(BaseComponent):
    """消息适配器
    
    根据给定的通信协议对智能体的输入输出进行格式化
    支持：
    - JSON 模式
    - 结构化 Markdown 段落
    - 纯文本段落格式
    - 用户自定义协议
    """
    
    PROTOCOL_TYPES = ["json", "markdown", "text", "custom"]
    
    def __init__(self, protocol_type: str = "json", **options):
        """初始化消息适配器
        
        Args:
            protocol_type: 协议类型
            **options: 其他配置参数
        """
        super().__init__(name=f"{protocol_type}_adapter")
        self.protocol_type = protocol_type
        self.options = options
        self.metadata["type"] = "MessageAdapter"
    
    def validate(self) -> bool:
        """验证适配器配置"""
        return (
            self.protocol_type in self.PROTOCOL_TYPES or
            self.protocol_type == "custom"
        )
    
    def format_input(self, data: Dict[str, Any]) -> str:
        """格式化输入数据"""
        if self.protocol_type == "json":
            import json
            return json.dumps(data)
        elif self.protocol_type == "markdown":
            lines = [f"**{k}**:\n>{v}\n" for k, v in data.items()]
            return "\n".join(lines)
        elif self.protocol_type == "text":
            return "\n".join(f"{k}: {v}" for k, v in data.items())
        else:
            # 自定义协议
            return str(data)
    
    def parse_output(self, output: str) -> Dict[str, Any]:
        """解析输出字符串
        
        Returns:
            解析后的字典
        """
        if self.protocol_type == "json":
            import json
            try:
                return json.loads(output)
            except Exception:
                return {"raw_output": output}
        elif self.protocol_type in ["markdown", "text"]:
            # 简单文本解析
            lines = output.split("\n")
            result = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip()] = value.strip()
            return result
        else:
            return {"result": output}

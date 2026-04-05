"""Vibe Graphing 设计缓存

管理 VibeGraph 的设计缓存，支持：
- JSON 格式存储
- 缓存加载与保存
- 版本管理
"""

import json
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional


class DesignCache:
    """VibeGraph 设计缓存管理器
    
    负责图设计的持久化和加载
    """
    
    def __init__(self, cache_path: str = "./cache/graph_designs"):
        """初始化缓存管理器
        
        Args:
            cache_path: 缓存目录路径
        """
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_cache_key(self, config_hash: str) -> str:
        """生成缓存文件名
        
        Args:
            config_hash: 配置哈希
            
        Returns:
            缓存文件名 (带 .json 扩展名)
        """
        safe_hash = hashlib.md5(config_hash.encode()).hexdigest()[:16]
        return f"{safe_hash}.json"
    
    def get_cache_path(self, config: Dict[str, Any]) -> Path:
        """获取缓存文件路径
        
        Args:
            config: 配置字典
            
        Returns:
            缓存文件路径
        """
        config_str = json.dumps(config, ensure_ascii=False)
        config_key = hashlib.md5(config_str.encode()).hexdigest()
        cache_file = self._generate_cache_key(config_key)
        return self.cache_path / cache_file
    
    def load(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从文件加载设计
        
        Args:
            file_path: 缓存文件路径
            
        Returns:
            设计字典或 None
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Cache load error: {e}")
            return None
    
    def save(self, config: Dict[str, Any], file_path: Path) -> bool:
        """保存设计到文件
        
        Args:
            config: 设计配置
            file_path: 文件路径
            
        Returns:
            成功返回 True
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 添加元数据
            meta = {
                "cached_at": self._get_timestamp(),
                "config_hash": hashlib.md5(
                    json.dumps(config, ensure_ascii=False).encode()
                ).hexdigest()[:16]
            }
            
            # 更新文件内容
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({**config, "_meta": meta}, f, ensure_ascii=False, indent=2)
            
            return True
            
        except IOError as e:
            print(f"Cache save error: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def invalidate(self, file_path: Path) -> bool:
        """使缓存失效（删除）
        
        Args:
            file_path: 缓存文件路径
            
        Returns:
            成功返回 True
        """
        try:
            if file_path.exists():
                file_path.unlink()
            return True
        except IOError:
            return False


class GraphDesignMetadata:
    """图设计元数据"""
    
    def __init__(self, user_intent: str, role_count: int, node_count: int):
        """初始化元数据
        
        Args:
            user_intent: 用户意图
            role_count: 角色数量
            node_count: 节点数量
        """
        self.user_intent = user_intent
        self.role_count = role_count
        self.node_count = node_count
        self.created_at = self._get_timestamp()
        self.generated_at = None
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_intent": self.user_intent,
            "role_count": self.role_count,
            "node_count": self.node_count,
            "created_at": self.created_at,
            "generated_at": self.generated_at
        }

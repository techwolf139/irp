"""Vibe Graphing Stage Components

实现 Vibe Graphing 三阶段流水线：
- Stage 1: 角色分配 (Role Assignment)
- Stage 2: 拓扑设计 (Topology Design)
- Stage 3: 语义补全 (Semantic Completion)
"""

from typing import Any, Callable, Dict, List, Optional


class RoleAssigner:
    """角色分配器
    
    将用户意图映射为一组具有明确责任边界的候选智能体
    """
    
    def __init__(self, build_model: Any = None):
        """初始化角色分配器
        
        Args:
            build_model: 用于生成角色分配的模型
        """
        self.build_model = build_model
    
    async def assign_roles(self, user_intent: str) -> List[Dict[str, Any]]:
        """分配角色
        
        Args:
            user_intent: 用户的自然语言意图
            
        Returns:
            角色列表，每个角色包含：
            - name: 角色名称
            - description: 角色描述
            - skills: 所需技能
            - instructions: 系统提示
        """
        # 简化版：根据常见模式进行角色分配
        role_patterns = {
            "approval": [
                {"name": "审批员", "role": "approver", "skills": ["合同审核", "风险评估"]},
                {"name": "法务", "role": "legal_reviewer", "skills": ["法律合规", "条款审查"]},
                {"name": "财务", "role": "finance_reviewer", "skills": ["预算审核", "支付流程"]},
            ],
            "review": [
                {"name": "代码审查员", "role": "code_reviewer", "skills": ["代码质量", "安全审计"]},
                {"name": "架构师", "role": "architect", "skills": ["系统设计", "架构评估"]},
            ],
            "analysis": [
                {"name": "数据分析师", "role": "data_analyst", "skills": ["数据分析", "数据可视化"]},
                {"name": "业务分析师", "role": "business_analyst", "skills": ["业务理解", "流程梳理"]},
            ],
        }
        
        # 根据关键词匹配角色模式
        intent_lower = user_intent.lower()
        for pattern, roles in role_patterns.items():
            if pattern in intent_lower:
                return roles
        
        # 默认返回通用角色
        return [
            {"name": "智能体顾问", "role": "advisor", "skills": ["通用知识", "问题解决"]},
        ]
    
    def validate_roles(self, roles: List[Dict[str, Any]]) -> bool:
        """验证角色分配
        
        Returns:
            有效返回 True
        """
        if not roles:
            return False
        
        for role in roles:
            if not role.get("name") or not role.get("role"):
                return False
        
        return True


class TopologyDesigner:
    """拓扑设计器
    
    基于智能体间的信息依赖关系和控制约束，
    生成有向图拓扑骨架
    """
    
    def __init__(self, build_model: Any = None):
        """初始化拓扑设计器
        
        Args:
            build_model: 用于生成图拓扑的模型
        """
        self.build_model = build_model
    
    def design_topology(self, roles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """设计拓扑结构
        
        Args:
            roles: 角色列表
            
        Returns:
            图拓扑描述：
            - nodes: 节点定义
            - edges: 边定义
            - metadata: 拓扑信息
        """
        # 简化版：生成线性拓扑
        node_ids = []
        for i, role in enumerate(roles):
            node_id = f"node_{role['role']}_{i}"
            node_ids.append(node_id)
        
        # 创建边连接
        edges = []
        for i in range(len(node_ids) - 1):
            edges.append({
                "source": node_ids[i],
                "target": node_ids[i + 1]
            })
        
        # 添加 ENTRY 和 EXIT 节点
        edges.insert(0, {
            "source": "ENTRY",
            "target": node_ids[0]
        })
        
        if node_ids:
            edges.append({
                "source": node_ids[-1],
                "target": "EXIT"
            })
        
        return {
            "nodes": [{"id": nid, "role": "agent"} for nid in node_ids],
            "edges": edges,
            "metadata": {
                "type": "linear_graph",
                "node_count": len(node_ids),
                "edge_count": len(edges)
            }
        }
    
    def validate_topology(self, topology: Dict[str, Any]) -> bool:
        """验证拓扑结构
        
        Returns:
            有效返回 True
        """
        if not topology.get("nodes") or not topology.get("edges"):
            return False
        
        # 检查是否有 ENTRY 和 EXIT
        edge_sources = [e["source"] for e in topology.get("edges", [])]
        edge_targets = [e["target"] for e in topology.get("edges", [])]
        
        return "ENTRY" in edge_sources and "EXIT" in edge_targets


class SemanticCompleter:
    """语义补全器
    
    对拓扑骨架进行参数化实例化，
    为每个结点配置提示词和工具
    """
    
    def __init__(self, build_model: Any = None):
        """初始化语义补全器
        
        Args:
            build_model: 用于生成节点配置的模型
        """
        self.build_model = build_model
    
    def complete_semantics(self, 
                          topology: Dict[str, Any], 
                          roles: List[Dict[str, Any]],
                          user_intent: str) -> Dict[str, Any]:
        """补全节点语义
        
        Args:
            topology: 拓扑结构
            roles: 角色定义
            user_intent: 用户意图
            
        Returns:
            完整的节点配置：
            - nodes: 带配置的节点
            - final_edges: 最终边列表
        """
        # 为每个节点添加详细配置
        configured_nodes = []
        for node_data in topology.get("nodes", []):
            node_id = node_data["id"]
            
            # 查找对应的角色信息
            role_info = None
            for i, role in enumerate(roles):
                if f"node_{role['role']}_{i}" == node_id or role["role"] in node_id:
                    role_info = role
                    break
            
            # 构建节点配置
            node_config = {
                "id": node_id,
                "type": "Agent",
                "instructions": self._generate_instructions(node_id, role_info, user_intent),
                "input_fields": [],
                "output_fields": [],
                "tools": []
            }
            configured_nodes.append(node_config)
        
        return {
            "nodes": configured_nodes,
            "edges": topology.get("edges", []),
            "metadata": {
                "user_intent": user_intent,
                "role_count": len(roles),
                "node_count": len(configured_nodes)
            }
        }
    
    def _generate_instructions(self, node_id: str, role_info: Optional[Dict], user_intent: str) -> str:
        """生成节点指令
        
        Returns:
            智能体系统提示
        """
        base_template = """
你是 {role_name}。

基于用户意图：{user_intent}

任务要求:
1. 理解用户的需求和上下文
2. 根据角色职责执行相应操作
3. 生成结构化输出供下游节点使用

输出格式要求:
- 清晰明确
- 包含必要信息
- 遵循指定格式

请开始执行任务。
"""
        
        role_name = role_info.get("name", "智能体") if role_info else "通用智能体"
        
        return base_template.format(
            role_name=role_name,
            user_intent=user_intent
        )


class VibeGraphStages:
    """Vibe Graphing 三阶段流水线"""
    
    def __init__(self, build_model: Any = None):
        """初始化流水线
        
        Args:
            build_model: 构建模型
        """
        self.role_assigner = RoleAssigner(build_model)
        self.topology_designer = TopologyDesigner(build_model)
        self.semantic_completer = SemanticCompleter(build_model)
    
    async def execute_pipeline(self, user_intent: str) -> Dict[str, Any]:
        """执行三阶段流水线
        
        Args:
            user_intent: 用户自然语言意图
            
        Returns:
            完整的图配置
        """
        # Stage 1: 角色分配
        print("Stage 1: Role Assignment")
        print("=" * 50)
        
        roles = await self.role_assigner.assign_roles(user_intent)
        print(f"Assigned {len(roles)} roles")
        if not self.role_assigner.validate_roles(roles):
            raise ValueError("Role assignment failed validation")
        
        # Stage 2: 拓扑设计
        print("\nStage 2: Topology Design")
        print("=" * 50)
        
        topology = self.topology_designer.design_topology(roles)
        print(f"Designed {len(topology.get('nodes', []))} nodes")
        if not self.topology_designer.validate_topology(topology):
            raise ValueError("Topology validation failed")
        
        # Stage 3: 语义补全
        print("\nStage 3: Semantic Completion")
        print("=" * 50)
        
        final_config = self.semantic_completer.complete_semantics(
            topology=topology,
            roles=roles,
            user_intent=user_intent
        )
        print(f"Completed {len(final_config['nodes'])} nodes with configurations")
        
        return final_config

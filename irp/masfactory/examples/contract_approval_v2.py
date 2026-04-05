"""VibeGraph 合同审批示例

演示如何使用 VibeGraph 实现合同审批工作流
"""

from pathlib import Path
from typing import Any, Dict, Optional
import os
import json

from irp.mas_factory.core.graph import Graph
from irp.mas_factory.core.agent import Agent, AgentDefinition
from irp.mas_factory.core.state import State
from irp.mas_factory.core.loop import Loop


class ContractApprovalGraph(Graph):
    """基于 VibeGraph 的合同审批工作流
    
    根据合同类型自动分配审批流程：
    - PURCHASE (采购合同): 采购负责人 → 法务 → 财务
    - OUTSOURCE (外包合同): 项目负责人 → 法务
    - FRAMEWORK (框架协议): 法务
    """
    
    def __init__(self, name: str = "contract_approval"):
        super().__init__(name=name)
        
        # 初始化审批节点
        self._init_approvers()
        
        # 创建路由节点
        self._init_routing()
        
        # 添加所有边
        self._create_edges()
    
    def _init_approvers(self) -> None:
        """初始化审批人节点"""
        # 创建不同角色的智能体节点
        roles = [
            "采购员", "采购负责人", "项目负责人", "法务", "财务"
        ]
        
        for role in roles:
            agent_def = AgentDefinition(
                name=f"{role}_approver",
                description=f"{role} - 负责审批相关业务",
                skills=["合同审核", "风险评估"],
                instructions=f"""你是 {role}，职责是：
                    1. 审核合同内容
                    2. 评估业务风险
                    3. 给出审批意见
                """
            )
            
            node = Agent(
                name=f"node_{role}",
                agent_def=agent_def
            )
            self.create_node(f"node_{role}", node)
    
    def _init_routing(self) -> None:
        """初始化路由节点"""
        # 创建类型路由器
        type_router_def = AgentDefinition(
            name="type_router",
            description="合同类型路由器 - 根据合同类型分配审批流程",
            skills=["路由", "类型识别"],
            instructions="""你是合同类型路由器。根据合同类型自动分配审批流程：
                - 采购合同 (PURCHASE): 采购负责人 → 法务 → 财务
                - 外包合同 (OUTSOURCE): 项目负责人 → 法务
                - 框架协议 (FRAMEWORK): 法务
                
                请根据输入的 contract_type 字段做出判断
            """
        )
        
        type_router = Agent(
            name="node_type_router",
            agent_def=type_router_def
        )
        self.create_node("node_type_router", type_router)
    
    def _create_edges(self) -> None:
        """创建工作流边"""
        # ENTRY → 类型路由器
        self.create_edge("ENTRY", "node_type_router")
        
        # 类型路由器 → 角色审批节点
        self.create_edge("node_type_router", "node_采购负责人")
        self.create_edge("node_type_router", "node_项目负责人")
        self.create_edge("node_type_router", "node_法务")
        
        # 角色审批 → 法务 (采购合同)
        self.create_edge("node_采购负责人", "node_法务")
        
        # 角色审批 → 财务 (采购合同)
        self.create_edge("node_法务", "node_财务")
        
        # Role 审批 → EXIT
        self.create_edge("node_财务", "EXIT")
        self.create_edge("node_法务", "EXIT")
    
    async def execute_contract_approval(self,
                                       contract_type: str,
                                       contract_id: str,
                                       amount: float,
                                       title: str = "",
                                       initial_state: Optional[Dict] = None) -> Dict[str, Any]:
        """执行合同审批流程
        
        Args:
            contract_type: 合同类型 (PURCHASE/OUTSOURCE/FRAMEWORK)
            contract_id: 合同 ID
            amount: 金额
            title: 合同标题
            initial_state: 初始状态
            
        Returns:
            审批结果
        """
        initial_data = initial_state or {
            "contract_type": contract_type,
            "contract_id": contract_id,
            "amount": amount,
            "title": title,
            "approval_status": "pending"
        }
        
        return await self.execute(initial_data)


async def demo_contract_approval_v2():
    """演示 VibeGraph 合同审批 v2

    Returns:
        审批结果
    """
    print("=" * 50)
    print("合同审批 VibeGraph 演示")
    print("=" * 50)
    
    # 创建审批图
    approval_graph = ContractApprovalGraph(name="purchase_contract_flow")
    
    # 执行审批
    result = await approval_graph.execute_contract_approval(
        contract_type="PURCHASE",
        contract_id="CON2024001",
        amount=100000.0,
        title="2024 年 Q1 设备采购"
    )
    
    print("\n审批结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result


if __name__ == "__main__":
    import asyncio
    
    asyncio.run(demo_contract_approval_v2())
